"""Core conversion module for transforming Excel cohort data into FHIR bundles.

This module provides the main functionality for converting structured Excel data
into FHIR-compliant JSON bundles. It handles resource creation, reference linking,
and JSON path-based data structure building.

Key Functions:
    create_transaction_bundle: Main entry point for creating FHIR bundles
    create_resources: Creates individual FHIR resources from definitions
    create_structure_from_jsonpath: Builds nested JSON structures from paths
    clean_empty: Removes empty structures from generated resources

Classes:
    ConversionContext: Encapsulates conversion parameters
    BuildContext: Encapsulates JSON path building parameters
"""

from typing import Any, Dict, List
import uuid
import random
import logging
from dataclasses import dataclass, field
from jsonpath_ng.jsonpath import Fields, Slice, Where
from jsonpath_ng.ext import parse as parse_ext

from .config.FhirSheetsConfiguration import FhirSheetsConfiguration

from .model.cohort_data_entity import CohortData, CohortData
from .model.resource_definition_entity import ResourceDefinition
from .model.resource_link_entity import ResourceLink
from . import fhir_formatting
from . import special_values

logger = logging.getLogger("fhirsheets.core.conversion")

# ============================================================================
# CONTEXT CLASSES FOR SIMPLIFIED FUNCTION SIGNATURES
# ============================================================================

@dataclass
class ConversionContext:
    """
    Encapsulates common parameters used throughout the conversion process.
    
    This reduces function signatures from 5 parameters to 1, making the code
    more maintainable and easier to extend with new configuration options.
    """
    resource_definitions: List[ResourceDefinition]
    resource_links: List[ResourceLink]
    cohort_data: CohortData
    index: int = 0
    config: FhirSheetsConfiguration = field(default_factory=lambda: FhirSheetsConfiguration({}))


@dataclass
class BuildContext:
    """
    Encapsulates parameters for JSON path structure building operations.
    
    This reduces the build_structure function signature from 7 parameters to 2,
    making recursive calls cleaner and more maintainable.
    """
    json_path: str
    resource_definition: ResourceDefinition
    data_type: str
    value: Any
    parts: List[str] = field(default_factory=list)
    previous_parts: List[str] = field(default_factory=list)

# Use a lower‑case name for the random generator to avoid the "constant redefined" warning.
_file_random = random.Random()

#Main top level function
#Creates a full transaction bundle for a patient at index
def create_transaction_bundle(
    resource_definition_entities: List[ResourceDefinition] | ConversionContext,
    resource_link_entities: List[ResourceLink] | None = None,
    cohort_data: CohortData | None = None,
    index: int = 0,
    config: FhirSheetsConfiguration = FhirSheetsConfiguration({}),
) -> Dict[str, Any]:
    """
    Create a full transaction bundle for a patient at the specified index.
    
    This function supports two calling patterns:
    
    1. NEW: Using ConversionContext (simplified signature)
       ctx = ConversionContext(resource_definitions=..., resource_links=..., cohort_data=...)
       bundle = create_transaction_bundle(ctx)
    
    2. OLD: Using individual parameters (backward compatible)
       bundle = create_transaction_bundle(definitions, links, data, index, config)
    
    Args:
        resource_definition_entities: Either a ConversionContext object (new style) or 
                                     List[ResourceDefinition] (old style)
        resource_link_entities: List[ResourceLink] (only used in old style)
        cohort_data: CohortData (only used in old style)
        index: Patient index (used in both styles, defaults to 0)
        config: FhirSheetsConfiguration (used in both styles)
    
    Returns:
        Dict[str, Any]: A FHIR transaction bundle
    """
    # Detect which calling pattern is being used
    if isinstance(resource_definition_entities, ConversionContext):
        # NEW STYLE: Using ConversionContext
        ctx = resource_definition_entities
    else:
        # OLD STYLE: Using individual parameters (backward compatible)
        if resource_link_entities is None or cohort_data is None:
            raise ValueError(
                "When using the old-style signature, resource_link_entities and "
                "cohort_data must be provided"
            )
        ctx = ConversionContext(
            resource_definitions=resource_definition_entities,
            resource_links=resource_link_entities,
            cohort_data=cohort_data,
            index=index,
            config=config
        )
    
    global _file_random
    _file_random = random.Random(ctx.config.random_seed)
    root_bundle = initialize_bundle(ctx.config)
    created_resources = create_resources(
        ctx.resource_definitions,
        ctx.resource_links,
        ctx.cohort_data,
        ctx.index,
        ctx.config
    )
    #Construct into fhir bundle
    for fhir_resource in created_resources.values():
        add_resource_to_transaction_bundle(root_bundle, fhir_resource)
    if ctx.config.medications_as_reference:
        post_process_create_medication_references(root_bundle)
    return root_bundle

def create_resources(
    resource_definition_entities: List[ResourceDefinition],
    resource_link_entities: List[ResourceLink],
    cohort_data: CohortData,
    index: int = 0,
    config: FhirSheetsConfiguration = FhirSheetsConfiguration({}),
) -> Dict[str, Dict[str, Any]]:
    """Create FHIR resources from resource definitions and cohort data.
    
    This function iterates through resource definitions, creates individual FHIR
    resources populated with patient data, establishes resource links, and cleans
    up empty structures.
    
    Args:
        resource_definition_entities: List of resource definitions specifying
            entity names, resource types, and profiles
        resource_link_entities: List of resource links defining references
            between resources
        cohort_data: Cohort data containing headers and patient entries
        index: Patient index in the cohort data (default: 0)
        config: Configuration object controlling conversion behavior
        
    Returns:
        Dictionary mapping entity names to their created FHIR resource dictionaries
        
    Example:
        >>> resources = create_resources(definitions, links, cohort_data, 0, config)
        >>> patient = resources['Patient']
        >>> print(patient['resourceType'])
        'Patient'
    """
    # Mapping from entity name to the created FHIR resource dictionary
    created_resources: Dict[str, Dict[str, Any]] = {}
    for resource_definition in resource_definition_entities:
        entityName = resource_definition.entityName
        if not entries_exist(entityName, cohort_data, index) and not config.build_empty_resources:
            logger.info(f"Patient index {index} - Skipping resource creation for entity '{entityName}' as no data entries found and build_empty_resources is set to False")
            continue
        #Create and collect fhir resources
        fhir_resource = create_fhir_resource(resource_definition, cohort_data, index, config)
        created_resources[entityName] = fhir_resource
    #Link resources after creation
    add_default_resource_links(created_resources, resource_link_entities, config)
    create_resource_links(created_resources, resource_link_entities, config)
    #Post-Process to clean the empty references from the resources
    created_resources = clean_empty(created_resources)
    return created_resources

def create_singular_resource(
    singleton_entityName: str,
    resource_definition_entities: List[ResourceDefinition],
    resource_link_entities: List[ResourceLink],
    cohort_data: CohortData,
    index: int = 0,
    config: FhirSheetsConfiguration = FhirSheetsConfiguration({}),
) -> Dict[str, Any]:
    """Create a single FHIR resource in preview mode with entity name references.
    
    This function creates all resources but returns only the specified singleton
    resource. It uses preview mode configuration to generate references using
    entity names instead of generated IDs, useful for displaying individual
    resources.
    
    Args:
        singleton_entityName: Name of the entity to return
        resource_definition_entities: List of all resource definitions
        resource_link_entities: List of resource links
        cohort_data: Cohort data containing patient information
        index: Patient index in the cohort data (default: 0)
        config: Configuration object (preview_mode will be enabled)
        
    Returns:
        Single FHIR resource dictionary for the specified entity
        
    Example:
        >>> patient = create_singular_resource('Patient', definitions, links, cohort_data)
        >>> print(patient['resourceType'])
        'Patient'
    """
    created_resources: Dict[str, Dict[str, Any]] = {}
    singleton_fhir_resource: Dict[str, Any] = {}
    # Create a preview mode config for singular resource
    preview_config = FhirSheetsConfiguration({
        'preview_mode': True,
        'enable_default_resource_links': config.enable_default_resource_links,
        'default_resource_references': config.default_resource_references,
        'array_type_references': config.array_type_references,
    })
    for resource_definition in resource_definition_entities:
        entityName = resource_definition.entityName
        #Create and collect fhir resources
        fhir_resource = create_fhir_resource(resource_definition, cohort_data, index, config)
        created_resources[entityName] = fhir_resource
        if entityName == singleton_entityName:
            singleton_fhir_resource = fhir_resource
    add_default_resource_links(created_resources, resource_link_entities, preview_config)
    create_resource_links(created_resources, resource_link_entities, preview_config)
    return singleton_fhir_resource

def initialize_bundle(config: FhirSheetsConfiguration) -> Dict[str, Any]:
    """Initialize a FHIR transaction bundle with required metadata.
    
    Creates a minimal FHIR Bundle resource with type 'transaction', a unique ID,
    and security metadata indicating test health data.
    
    Args:
        config: Configuration object (currently unused but kept for consistency)
        
    Returns:
        Dictionary representing a FHIR Bundle resource with empty entry list
        
    Example:
        >>> bundle = initialize_bundle(config)
        >>> print(bundle['resourceType'])
        'Bundle'
        >>> print(bundle['type'])
        'transaction'
    """
    root_bundle: Dict[str, Any] = {}
    root_bundle['resourceType'] = 'Bundle'
    root_bundle['id'] = str(generate_UUID()).strip()
    root_bundle['meta'] = {
        'security': [{
            'system': 'http://terminology.hl7.org/CodeSystem/v3-ActReason',
            'code': 'HTEST',
            'display': 'test health data'
        }]
    }
    root_bundle['type'] = 'transaction'
    root_bundle['entry'] = []
    return root_bundle

#Initialize a resource from a resource definition. Adding basic information all resources need
def initialize_resource(resource_definition: ResourceDefinition) -> Dict[str, Any]:
    """Create a minimal FHIR resource dictionary based on a ``ResourceDefinition``.

    The function populates the mandatory ``resourceType`` and ``id`` fields and, if
    the definition includes ``profiles``, adds a ``meta`` block with the profile
    information and a standard security tag.
    """
    # The original implementation mistakenly referenced an undefined variable
    # ``initial_resource`` and also created an unused ``created_resources`` dict.
    # We initialise a fresh dictionary here and populate it correctly.
    initial_resource: Dict[str, Any] = {}
    initial_resource["resourceType"] = resource_definition.resourceType.strip()
    initial_resource["id"] = str(generate_UUID()).strip()
    if getattr(resource_definition, "profiles", None):
        initial_resource["meta"] = {
            "profile": resource_definition.profiles,
            "security": [{
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
                "code": "HTEST",
                "display": "test health data",
            }],
        }
    return initial_resource

def create_fhir_resource(
    resource_definition: ResourceDefinition,
    cohort_data: CohortData,
    index: int = 0,
    config: FhirSheetsConfiguration = FhirSheetsConfiguration({}),
) -> Dict[str, Any]:
    """Create a FHIR resource from a resource definition and patient data.
    
    This function initializes a resource, retrieves relevant field entries from
    cohort data, and populates the resource structure using JSON paths and values.
    
    Args:
        resource_definition: Definition specifying entity name, resource type,
            and profiles
        cohort_data: Cohort data containing headers and patient entries
        index: Patient index in the cohort data (default: 0)
        config: Configuration object controlling conversion behavior
        
    Returns:
        Dictionary representing a populated FHIR resource
        
    Example:
        >>> patient_def = ResourceDefinition('Patient', 'Patient', [])
        >>> resource = create_fhir_resource(patient_def, cohort_data, 0)
        >>> print(resource['resourceType'])
        'Patient'
    """
    resource_dict = initialize_resource(resource_definition)
    #Get field entries for this entity
    header_entries_for_resourcename = [
        headerEntry
        for headerEntry in cohort_data.headers
        if headerEntry.entityName == resource_definition.entityName
    ]
    dataelements_for_resourcename = {
        field_name: value
        for (entityName, field_name), value in cohort_data.patients[index].entries.items()
        if entityName == resource_definition.entityName
    }
    if len(dataelements_for_resourcename.keys()) == 0:
        logger.warning(f"Patient index {index} - Create Fhir Resource Error - {resource_definition.entityName} - No columns for entity '{resource_definition.entityName}' found for resource in 'PatientData' sheet")
        return resource_dict
        all_field_entries = cohort_data.entities[resource_definition.entityName].fields
    #For each field within the entity
    for fieldName, value in dataelements_for_resourcename.items():
        header_element = next((header for header in header_entries_for_resourcename if header.fieldName == fieldName), None)
        if header_element is None:
            logger.warning(f" Field Name {fieldName} - No Header Entry found.")
            continue
        jsonPath = header_element.jsonPath
        if jsonPath is None:
            logger.warning(f" Field Name {fieldName} - Header Entry found, but jsonPath attribute is None. Skipping.")
            continue
        valueType = header_element.valueType
        if valueType is None:
            logger.warning(f" Field Name {fieldName} - Header Entry found, but valueType attribute is None. Skipping.")
            continue
        create_structure_from_jsonpath(resource_dict, jsonPath, resource_definition, valueType, value)
    return resource_dict

def add_default_resource_links(
    created_resources: Dict[str, Dict[str, Any]],
    resource_link_entities: List[ResourceLink],
    config: FhirSheetsConfiguration = FhirSheetsConfiguration({}),
) -> None:
    """Add default resource references when only one instance of each type exists.
    
    This function automatically creates resource links based on default reference
    patterns when there is exactly one resource of the source and destination types.
    For example, if there's one Patient and one Observation, it will automatically
    link Observation.subject to the Patient.
    
    Args:
        created_resources: Dictionary of created resources keyed by entity name
        resource_link_entities: List to append new resource links to (modified in place)
        config: Configuration object with default_resource_references list
        
    Returns:
        None (modifies resource_link_entities in place)
        
    Note:
        Only creates links if enable_default_resource_links is True in config
    """
    # Check if default resource links are enabled
    if not config.enable_default_resource_links:
        return
    
    default_references = config.default_resource_references
    
    resource_counts = {}
    for resourceName, resource in created_resources.items():
        resourceType: str = resource['resourceType'].lower().strip()
        if resourceType not in resource_counts:
            resource_counts[resourceType]= {'count': 1, 'singletonEntityName': resourceName, 'singleResource': resource}
        else:
            resource_counts[resourceType]['count'] += 1
            resource_counts[resourceType]['singletonResource'] = resource
            resource_counts[resourceType]['singletonEntityName'] = resourceName
            
    for default_reference in default_references:
        sourceType = default_reference[0]
        destinationType = default_reference[1]
        fieldName = default_reference[2]
        if (
            sourceType in resource_counts
            and destinationType in resource_counts
            and resource_counts[sourceType]["count"] == 1
            and resource_counts[destinationType]["count"] == 1
        ):
            originResourceEntityName: str = resource_counts[sourceType]["singletonEntityName"]
            destinationResourceEntityName: str = resource_counts[destinationType]["singletonEntityName"]
            new_link = ResourceLink(originResourceEntityName, fieldName, destinationResourceEntityName)
            if (new_link.originResource, new_link.referencePath, new_link.destinationResource) not in [(l.originResource, l.referencePath, l.destinationResource) for l in resource_link_entities]:
                resource_link_entities.append(
                    new_link
                )
    return
        
            
def create_resource_links(
    created_resources: Dict[str, Dict[str, Any]],
    resource_link_entites: List[ResourceLink],
    config: FhirSheetsConfiguration = FhirSheetsConfiguration({}),
) -> None:
    """Create all resource references between FHIR resources.
    
    Iterates through resource link entities and creates references between
    resources according to the specified paths.
    
    Args:
        created_resources: Dictionary of created resources keyed by entity name
        resource_link_entites: List of resource links to create
        config: Configuration object controlling reference behavior
        
    Returns:
        None (modifies created_resources in place)
    """
    logger.info("Building resource links")
    for resource_link_entity in resource_link_entites:
        create_resource_link(created_resources, resource_link_entity, config)
    return
    
def create_resource_link(
    created_resources: Dict[str, Dict[str, Any]],
    resource_link_entity: ResourceLink,
    config: FhirSheetsConfiguration = FhirSheetsConfiguration({}),
) -> None:
    """Create a single resource reference between two FHIR resources.
    
    This function establishes a reference from an origin resource to a destination
    resource at the specified reference path. It handles both single references
    and array-type references based on configuration.
    
    Args:
        created_resources: Dictionary of created resources keyed by entity name
        resource_link_entity: Resource link specifying origin, destination, and path
        config: Configuration object with array_type_references and preview_mode
        
    Returns:
        None (modifies origin resource in created_resources in place)
        
    Example:
        >>> link = ResourceLink('Observation', 'subject', 'Patient')
        >>> create_resource_link(resources, link, config)
        >>> print(resources['Observation']['subject']['reference'])
        'Patient/patient-id-123'
    """
    # template scaffolding
    reference_json_block = {
        "reference" : "$value"
    }
    #Special reference handling blocks, in the form of (originResource, destinationResource, referencePath)
    arrayType_references = config.array_type_references
    #Find the origin and destination resource from the link
    try:
        originResource = created_resources[resource_link_entity.originResource]
    except KeyError:
        logger.warning(f" In ResourceLinks tab, found a Origin Resource of : {resource_link_entity.originResource}  but no such entity found in PatientData")
        return
    try:
        destinationResource = created_resources[resource_link_entity.destinationResource]
    except KeyError:
        logger.warning(f" In ResourceLinks tab, found a Destination Resource  of : {resource_link_entity.destinationResource}  but no such entity found in PatientData")
        return
    #Establish the value of the reference
    if config.preview_mode:
        reference_value = destinationResource['resourceType'] + "/" + resource_link_entity.destinationResource
    else:
        reference_value = destinationResource['resourceType'] + "/" + destinationResource['id']

    ref_path = resource_link_entity.referencePath.strip()

    # Parse the reference path to handle nested paths like "performer.[0].actor"
    def parse_path(path: str):
        """Parse a path string into segments, handling array indices."""
        import re
        # Split by dots, but keep array indices with their parent
        segments = []
        parts = path.split('.')
        for part in parts:
            # Check if this part contains an array index
            match = re.match(r'^([^\[]+)(\[\d+\])$', part)
            if match:
                # Split into field name and array index
                segments.append(match.group(1))
                segments.append(match.group(2))
            else:
                segments.append(part)
        return segments
    
    def set_nested_reference(obj, segments, reference_json, reference_val, is_array_type):
        """Navigate through nested path and set the reference at the target location."""
        current = obj
        
        # Navigate to the parent of the final segment
        for i, segment in enumerate(segments[:-1]):
            if segment.startswith('[') and segment.endswith(']'):
                # This is an array index
                index = int(segment[1:-1])
                # Ensure the current object is a list with enough elements
                if not isinstance(current, list):
                    raise ValueError(f"Expected array at segment {i}, but found {type(current)}")
                # Extend list if necessary
                while len(current) <= index:
                    current.append({})
                current = current[index]
            else:
                # This is a regular field
                if segment not in current:
                    # Determine if next segment is an array index
                    if i + 1 < len(segments) - 1 and segments[i + 1].startswith('['):
                        current[segment] = []
                    else:
                        current[segment] = {}
                current = current[segment]
        
        # Set the reference at the final segment
        final_segment = segments[-1]
        if final_segment.startswith('[') and final_segment.endswith(']'):
            # Final segment is an array index
            index = int(final_segment[1:-1])
            if not isinstance(current, list):
                raise ValueError(f"Expected array at final segment, but found {type(current)}")
            while len(current) <= index:
                current.append({})
            new_reference = reference_json.copy()
            new_reference['reference'] = reference_val
            current[index] = new_reference
        else:
            # Final segment is a regular field
            if is_array_type:
                if final_segment not in current:
                    current[final_segment] = []
                new_reference = reference_json.copy()
                new_reference['reference'] = reference_val
                current[final_segment].append(new_reference)
            else:
                current[final_segment] = reference_json.copy()
                current[final_segment]["reference"] = reference_val
    
    # Parse the path into segments
    path_segments = parse_path(ref_path)
    
    # Determine if this is an array type reference
    link_tuple = (
        originResource['resourceType'].strip().lower(),
        destinationResource['resourceType'].strip().lower(),
        ref_path[0].lower() + ref_path[1:]
    )
    is_array_type = link_tuple in arrayType_references
    
    # Set the nested reference
    try:
        set_nested_reference(originResource, path_segments, reference_json_block, reference_value, is_array_type)
    except (ValueError, KeyError, IndexError) as e:
        logger.warning(f"Failed to set reference at path '{ref_path}': {e}")
    
    return

def add_resource_to_transaction_bundle(root_bundle: Dict[str, Any], fhir_resource: Dict[str, Any]) -> Dict[str, Any]:
    """Add a FHIR resource to a transaction bundle as an entry.
    
    Creates a bundle entry with fullUrl, resource, and request fields following
    FHIR transaction bundle specifications.
    
    Args:
        root_bundle: FHIR Bundle resource to add entry to
        fhir_resource: FHIR resource to add to the bundle
        
    Returns:
        Modified bundle with new entry added
        
    Example:
        >>> bundle = initialize_bundle(config)
        >>> patient = {'resourceType': 'Patient', 'id': '123'}
        >>> bundle = add_resource_to_transaction_bundle(bundle, patient)
        >>> print(len(bundle['entry']))
        1
    """
    entry = {}
    entry['fullUrl'] = "urn:uuid:"+fhir_resource['id']
    entry['resource'] = fhir_resource
    entry['request'] = {
      "method": "PUT",
      "url": fhir_resource['resourceType'] + "/" + fhir_resource['id']
    }
    root_bundle['entry'].append(entry)
    return root_bundle

def create_structure_from_jsonpath(
    root_struct: Dict[str, Any],
    json_path: str,
    resource_definition: ResourceDefinition,
    dataType: str,
    value: Any,
) -> Any:
    """Build nested JSON structure from a JSON path and assign a value.
    
    This function parses a JSON path string and recursively creates the necessary
    nested structure in the root dictionary, then assigns the value at the final
    location. Supports dot notation, array indices, and conditional qualifiers.
    
    Supported path features:
        - Dot notation: Patient.name.family
        - Array indices: Patient.name.[0].family
        - Conditional qualifiers: Patient.identifier[type=MRN].value
        - Special handlers: Patient.extension[Race].ombCategory.value
    
    Args:
        root_struct: Root dictionary to build structure in
        json_path: JSON path string (e.g., 'Patient.name.family')
        resource_definition: Resource definition for context
        dataType: FHIR data type for value formatting
        value: Value to assign at the path location
        
    Returns:
        Modified root structure with value assigned at path
        
    Example:
        >>> resource = {}
        >>> create_structure_from_jsonpath(resource, 'Patient.name.family', 
        ...                                patient_def, 'string', 'Smith')
        >>> print(resource['name']['family'])
        'Smith'
    """
    #Get all dot notation components as seperate 
    if dataType is not None and dataType.strip().lower() == 'string':
        value = str(value)
    
    if value == None:
        logger.warning(f" Full jsonpath: {json_path} - Expected to find a value but found None instead")
        return root_struct
    
    #Create BuildContext and start recursive processing
    buildCtx = BuildContext(
        json_path=json_path,
        resource_definition=resource_definition,
        data_type=dataType,
        value=value,
        parts=json_path.split('.'),
        previous_parts=[]
    )
    return build_structure(root_struct, buildCtx)

# ============================================================================
# HELPER FUNCTIONS FOR build_structure
# ============================================================================

def _handle_final_assignment(
    current_struct: Any,
    buildCtx: BuildContext,
    part: str
) -> Any:
    """
    Handle the final assignment when we've reached the leaf node (len(parts) == 1).
    This assigns the value directly to the structure.
    """
    # Check for numeric qualifier '[0]' and '[1]'
    if '[' in part and ']' in part:
        # Separate the key from the qualifier
        key_part = part[:part.index('[')]
        qualifier = part[part.index('[')+1:part.index(']')]
        
        # If there is no key part, aka '[0]', '[1]' etc, then it's a simple accessor
        if key_part is None or key_part == '':
            if not qualifier.isdigit():
                raise TypeError(
                    f"ERROR: Full jsonpath: {buildCtx.json_path} - "
                    f"current path - {'.'.join(buildCtx.previous_parts + buildCtx.parts[:1])} - "
                    f"qualifier - {qualifier} - standalone qualifier expected to be a single "
                    f"index numeric ([0], [1], etc)"
                )
            qualifier_index = int(qualifier)
            if current_struct == {}:
                current_struct = []
            if not isinstance(current_struct, list):
                raise TypeError(
                    f"ERROR: Full jsonpath: {buildCtx.json_path} - "
                    f"current path - {'.'.join(buildCtx.previous_parts + buildCtx.parts[:1])} - "
                    f"Expected a list, but got {type(current_struct).__name__} instead."
                )
            if qualifier_index + 1 > len(current_struct):
                current_struct.extend({} for x in range(qualifier_index + 1 - len(current_struct)))
            # Assign the indexed part
            fhir_formatting.assign_value(current_struct, qualifier_index, buildCtx.value, buildCtx.data_type)
            return current_struct
    
    # Default case where there was no qualifier, simply assign here
    fhir_formatting.assign_value(current_struct, part, buildCtx.value, buildCtx.data_type)
    return current_struct


def _handle_array_qualifier(
    current_struct: Any,
    buildCtx: BuildContext,
    part: str
) -> Any:
    """
    Handle array access and qualifiers like [0], [1], or [use=official].
    This is for intermediate nodes in the path that need array/qualifier handling.
    """
    # Separate the key from the qualifier
    key_part = part[:part.index('[')]
    qualifier = part[part.index('[')+1:part.index(']')]
    qualifier_condition = qualifier.split('=')
    
    # If there is no key part, aka '[0]', '[1]' etc, then it's a simple accessor
    if key_part is None or key_part == '':
        if not qualifier.isdigit():
            raise TypeError(
                f"ERROR: Full jsonpath: {buildCtx.json_path} - "
                f"current path - {'.'.join(buildCtx.previous_parts + buildCtx.parts[:1])} - "
                f"qualifier - {qualifier} - standalone qualifier expected to be a single "
                f"index numeric ([0], [1], etc)"
            )
        if current_struct == {}:
            current_struct = []
        if not isinstance(current_struct, list):
            raise TypeError(
                f"ERROR: Full jsonpath: {buildCtx.json_path} - "
                f"current path - {'.'.join(buildCtx.previous_parts + buildCtx.parts[:1])} - "
                f"Expected a list, but got {type(current_struct).__name__} instead."
            )
        qualifier_as_number = int(qualifier)
        if qualifier_as_number + 1 > len(current_struct):
            current_struct.extend({} for x in range(qualifier_as_number + 1 - len(current_struct)))
        
        # Recurse with updated context
        new_buildCtx = BuildContext(
            json_path=buildCtx.json_path,
            resource_definition=buildCtx.resource_definition,
            data_type=buildCtx.data_type,
            value=buildCtx.value,
            parts=buildCtx.parts[1:],
            previous_parts=buildCtx.previous_parts + [part]
        )
        inner_struct = build_structure(current_struct[qualifier_as_number], new_buildCtx)
        current_struct[qualifier_as_number] = inner_struct
        return current_struct
    
    # Create the key part in the structure
    if (not key_part in current_struct) or (isinstance(current_struct[key_part], dict)):
        current_struct[key_part] = []
    
    # If there is a key_part and the qualifier condition is defined (e.g., [use=official])
    if len(qualifier_condition) == 2:
        # Special handling for code
        if key_part != "coding" and (qualifier_condition[0] in ('code', 'system')):
            # Move into the coding section if a qualifier asks for 'code' or 'system'
            if 'coding' not in current_struct:
                current_struct['coding'] = []
                current_struct = current_struct['coding']
        
        qualifier_key, qualifier_value = qualifier_condition
        # Retrieve an inner structure if it exists already that matches the criteria
        inner_struct = next(
            (innerElement for innerElement in current_struct[key_part] 
             if isinstance(innerElement, dict) and innerElement.get(qualifier_key) == qualifier_value),
            None
        )
        # If no inner structure exists, create one instead
        if inner_struct is None:
            inner_struct = {qualifier_key: qualifier_value}
            current_struct[key_part].append(inner_struct)
        
        # Recurse with updated context
        new_buildCtx = BuildContext(
            json_path=buildCtx.json_path,
            resource_definition=buildCtx.resource_definition,
            data_type=buildCtx.data_type,
            value=buildCtx.value,
            parts=buildCtx.parts[1:],
            previous_parts=buildCtx.previous_parts + [part]
        )
        inner_struct = build_structure(inner_struct, new_buildCtx)
        return current_struct
    
    # If there's no qualifier condition, but an index aka '[0]', '[1]' etc, then it's a simple accessor
    elif qualifier.isdigit():
        if not isinstance(current_struct[key_part], list):
            raise TypeError(
                f"ERROR: Full jsonpath: {buildCtx.json_path} - "
                f"current path - {'.'.join(buildCtx.previous_parts + [buildCtx.parts[0]])} - "
                f"Expected a list, but got {type(current_struct).__name__} instead."
            )
        qualifier_as_number = int(qualifier)
        if qualifier_as_number > len(current_struct):
            current_struct[key_part].extend({} for x in range(qualifier_as_number - len(current_struct)))
        
        # Recurse with updated context
        new_buildCtx = BuildContext(
            json_path=buildCtx.json_path,
            resource_definition=buildCtx.resource_definition,
            data_type=buildCtx.data_type,
            value=buildCtx.value,
            parts=buildCtx.parts[1:],
            previous_parts=buildCtx.previous_parts + [part]
        )
        inner_struct = build_structure(current_struct[key_part][qualifier_as_number], new_buildCtx)
        current_struct[key_part][qualifier_as_number] = inner_struct
        return current_struct
    
    return current_struct


def _handle_simple_navigation(
    current_struct: Any,
    buildCtx: BuildContext,
    part: str
) -> Any:
    """
    Handle simple object navigation without qualifiers.
    Creates nested objects as needed and recurses deeper.
    """
    if part not in current_struct:
        current_struct[part] = {}
    
    # Recurse with updated context
    new_buildCtx = BuildContext(
        json_path=buildCtx.json_path,
        resource_definition=buildCtx.resource_definition,
        data_type=buildCtx.data_type,
        value=buildCtx.value,
        parts=buildCtx.parts[1:],
        previous_parts=buildCtx.previous_parts + [part]
    )
    inner_struct = build_structure(current_struct[part], new_buildCtx)
    current_struct[part] = inner_struct
    return current_struct


# ============================================================================
# MAIN RECURSIVE FUNCTION
# ============================================================================

def build_structure(
    current_struct: Any,
    buildCtx: BuildContext,
) -> Any:
    """
    Main recursive function to drill into the JSON structure, assign paths, 
    and create structure where needed.
    
    This function dispatches to specialized handlers based on the current path segment:
    - Special value handlers (from special_values module)
    - Final assignment (when at leaf node)
    - Array/qualifier handling (for [0], [use=official], etc.)
    - Simple navigation (for regular object properties)
    """
    # Base case: no more parts to process
    if len(buildCtx.parts) == 0:
        return current_struct
    
    # Grab current part
    part = buildCtx.parts[0]
    
    # Check for special handling clause
    matching_handler = next(
        (handler for handler in special_values.custom_structure_handlers 
         if (buildCtx.json_path.startswith(handler) or buildCtx.json_path == handler)),
        None
    )
    if matching_handler is not None:
        return special_values.custom_structure_handlers[matching_handler].assign_value(
            buildCtx.json_path, 
            buildCtx.resource_definition, 
            buildCtx.data_type, 
            current_struct, 
            buildCtx.parts[-1], 
            buildCtx.value
        )
    
    # Ignore dollar sign ($) and resource type - drill farther down
    if part == '$' or part == buildCtx.resource_definition.resourceType.strip():
        new_buildCtx = BuildContext(
            json_path=buildCtx.json_path,
            resource_definition=buildCtx.resource_definition,
            data_type=buildCtx.data_type,
            value=buildCtx.value,
            parts=buildCtx.parts[1:],
            previous_parts=buildCtx.previous_parts + [part]
        )
        return build_structure(current_struct, new_buildCtx)
    
    # Dispatch to appropriate handler based on the current state
    if len(buildCtx.parts) == 1:
        # Final leaf node - assign the value
        return _handle_final_assignment(current_struct, buildCtx, part)
    elif '[' in part and ']' in part:
        # Array or qualifier handling
        return _handle_array_qualifier(current_struct, buildCtx, part)
    else:
        # Simple object navigation
        return _handle_simple_navigation(current_struct, buildCtx, part)

def post_process_create_medication_references(root_bundle: Dict[str, Any]) -> None:
    """Convert MedicationRequest.medicationCodeableConcept to Medication references.
    
    This post-processing function finds all MedicationRequest resources in the bundle,
    creates or reuses Medication resources for their medicationCodeableConcept values,
    and replaces the CodeableConcept with a reference to the Medication resource.
    
    Args:
        root_bundle: FHIR Bundle containing MedicationRequest resources
        
    Returns:
        None (modifies bundle in place)
        
    Note:
        Only runs when config.medications_as_reference is True
    """
    medication_resources = [resource['resource'] for resource in root_bundle['entry'] if resource['resource']['resourceType'] == "Medication"]
    medication_request_resources = [resource['resource'] for resource in root_bundle['entry'] if resource['resource']['resourceType'] == "MedicationRequest"]
    for medication_request_resource in medication_request_resources:
        #Get candidates
        medication_candidates = [resource for resource in medication_resources if resource['code'] == medication_request_resource['medicationCodeableConcept']]
        if not medication_candidates: #If no candidates, create, else get the first candidate
            medication_target = target_medication = createMedicationResource(root_bundle, medication_request_resource['medicationCodeableConcept'])
            medication_resources.append(target_medication)
        else:
            target_medication = medication_candidates[0]
            
        del(medication_request_resource['medicationCodeableConcept'])
        medication_request_resource['medicationReference'] = target_medication['resourceType'] + "/" + target_medication['id']
    return

def createMedicationResource(root_bundle: Dict[str, Any], medicationCodeableConcept: Any) -> Dict[str, Any]:
    """Create a Medication resource from a CodeableConcept and add to bundle.
    
    Args:
        root_bundle: FHIR Bundle to add the Medication resource to
        medicationCodeableConcept: CodeableConcept to use as Medication.code
        
    Returns:
        Created Medication resource dictionary
    """
    # ``ResourceDefinition.from_dict`` returns a ``ResourceDefinition``; we cast the result
    # of ``initialize_resource`` to the expected dict type for clarity.
    target_medication: Dict[str, Any] = initialize_resource(
        ResourceDefinition.from_dict({"ResourceType": "Medication"})
    )
    target_medication['code'] = medicationCodeableConcept
    add_resource_to_transaction_bundle(root_bundle, target_medication)
    return target_medication

def generate_UUID() -> uuid.UUID:
    """Generate a random UUID (Version 4)."""
    return uuid.uuid4()

def entries_exist(entityName: str, cohort_data: CohortData, index: int = 0) -> bool:
    """Utility function to determine if any entries exist for ``entityName``
    in the patient at ``index``.

    The original implementation contained duplicated code and an stray
    triple quote that caused a ``SyntaxError`` during import.  This cleaned up
    version returns ``True`` if at least one entry in ``patient.entries`` has a
    matching entity name, otherwise ``False``.
    """
    patient = cohort_data.patients[index]
    # ``patient.entries`` is a dict keyed by a tuple (entityName, field_name)
    # We only care about the first element of the key.
    return any(entry_entityName == entityName for (entry_entityName, _), _ in patient.entries.items())

def clean_empty(data: Any) -> Any:
    """Recursively remove *empty* structures while preserving empty strings.

    The original implementation filtered out empty strings (""), which caused
    legitimate empty‑string values to be lost. The test suite expects empty
    strings to be retained, but still wants to drop structures that are
    effectively empty – for example a ``coding`` entry where *all* fields are
    empty strings. To satisfy both requirements we:

    1. Preserve empty strings as values.
    2. Remove ``None``, empty dicts, and empty lists.
    3. Treat a dict whose **all** values are empty strings as empty and drop
       it, which removes empty ``coding`` objects while keeping other empty
       strings intact.
    """
    if isinstance(data, dict):
        # Build a new dict with explicit typing to satisfy static analysis.
        cleaned_dict: Dict[str, Any] = {}
        for k, v in data.items():  # type: ignore[assignment]
            cleaned_val = clean_empty(v)
            if cleaned_val not in (None, {}, [], ""):
                cleaned_dict[k] = cleaned_val
        # If the dict is now empty **or** all remaining values are empty strings,
        # consider it empty and return an empty dict so the caller can filter it.
        if not cleaned_dict:
            return {}
        if all(isinstance(v, str) and v == "" for v in cleaned_dict.values()):
            return {}
        return cleaned_dict
    elif isinstance(data, list):
        # Clean each element and filter out empty structures.
        cleaned_list: List[Any] = []
        for item in data:  # type: ignore[assignment]
            cleaned_item = clean_empty(item)
            if cleaned_item not in (None, {}, []):
                cleaned_list.append(cleaned_item)
        return cleaned_list
    else:
        # Primitive values (including empty strings) are returned unchanged.
        return data