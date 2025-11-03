from typing import Any, Dict, List
import uuid
from jsonpath_ng.jsonpath import Fields, Slice, Where
from jsonpath_ng.ext import parse as parse_ext

from .config.FhirSheetsConfiguration import FhirSheetsConfiguration

from .model.cohort_data_entity import CohortData, CohortData
from .model.resource_definition_entity import ResourceDefinition
from .model.resource_link_entity import ResourceLink
from . import fhir_formatting
from . import special_values

#Main top level function
#Creates a full transaction bundle for a patient at index
def create_transaction_bundle(resource_definition_entities: List[ResourceDefinition], resource_link_entities: List[ResourceLink], cohort_data: CohortData, index = 0, config: FhirSheetsConfiguration = FhirSheetsConfiguration({})):
    root_bundle = initialize_bundle()
    created_resources = {}
    for resource_definition in resource_definition_entities:
        entityName = resource_definition.entityName
        #Create and collect fhir resources
        fhir_resource = create_fhir_resource(resource_definition, cohort_data, index, config)
        created_resources[entityName] = fhir_resource
    #Link resources after creation
    add_default_resource_links(created_resources, resource_link_entities)
    create_resource_links(created_resources, resource_link_entities, config.preview_mode)
    #Construct into fhir bundle
    for fhir_resource in created_resources.values():
        add_resource_to_transaction_bundle(root_bundle, fhir_resource)
    if config.medications_as_reference:
        post_process_create_medication_references(root_bundle)
    return root_bundle

def create_singular_resource(singleton_entityName: str, resource_definition_entities: List[ResourceDefinition], resource_link_entities: List[ResourceLink], cohort_data: CohortData, index = 0):
    created_resources = {}
    singleton_fhir_resource = {}
    for resource_definition in resource_definition_entities:
        entityName = resource_definition.entityName
        #Create and collect fhir resources
        fhir_resource = create_fhir_resource(resource_definition, cohort_data, index)
        created_resources[entityName] = fhir_resource
        if entityName == singleton_entityName:
            singleton_fhir_resource = fhir_resource
    add_default_resource_links(created_resources, resource_link_entities)
    create_resource_links(created_resources, resource_link_entities, preview_mode=True)
    return singleton_fhir_resource

#Initialize root bundle definition
def initialize_bundle():
    root_bundle = {}
    root_bundle['resourceType'] = 'Bundle'
    root_bundle['id'] = str(uuid.uuid4())
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
def initialize_resource(resource_definition):
    initial_resource = {}
    initial_resource['resourceType'] = resource_definition.resourceType.strip()
    initial_resource['id'] = str(uuid.uuid4()).strip()
    if resource_definition.profiles:
        initial_resource['meta'] = {
            'profile': resource_definition.profiles,
            'security': [{
                'system': 'http://terminology.hl7.org/CodeSystem/v3-ActReason',
                'code': 'HTEST',
                'display': 'test health data'
            }]
        }
    return initial_resource

# Creates a fhir-json structure from a resource definition entity and the patient_data_sheet
def create_fhir_resource(resource_definition: ResourceDefinition, cohort_data: CohortData, index: int = 0, config: FhirSheetsConfiguration = FhirSheetsConfiguration({})) -> dict:
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
        print(f"WARNING: Patient index {index} - Create Fhir Resource Error - {resource_definition.entityName} - No columns for entity '{resource_definition.entityName}' found for resource in 'PatientData' sheet")
        return resource_dict
        all_field_entries = cohort_data.entities[resource_definition.entityName].fields
    #For each field within the entity
    for fieldName, value in dataelements_for_resourcename.items():
        header_element = next((header for header in header_entries_for_resourcename if header.fieldName == fieldName), None)
        if header_element is None:
            print(f"WARNING: Field Name {fieldName} - No Header Entry found.")
            continue
        jsonPath = header_element.jsonPath
        if jsonPath is None:
            print(f"WARNING: Field Name {fieldName} - Header Entry found, but jsonPath attribute is None. Skipping.")
            continue
        valueType = header_element.valueType
        if valueType is None:
            print(f"WARNING: Field Name {fieldName} - Header Entry found, but valueType attribute is None. Skipping.")
            continue
        create_structure_from_jsonpath(resource_dict, jsonPath, resource_definition, valueType, value)
    return resource_dict

#Create a resource_link for default references in the cases where only 1 resourceType of the source and destination exist
def add_default_resource_links(created_resources: dict, resource_link_entities: List[ResourceLink]):
    default_references = [
        ('allergyintolerance', 'patient', 'patient'),
        ('allergyintolerance', 'practitioner', 'asserter'),
        ('careplan', 'goal', 'goal'),
        ('careplan', 'patient', 'subject'),
        ('careplan', 'practitioner', 'performer'),
        ('diagnosticreport', 'careteam', 'performer'),
        ('diagnosticreport', 'imagingStudy', 'imagingStudy'),
        ('diagnosticreport', 'observation', 'result'),
        ('diagnosticreport', 'organization', 'performer'),
        ('diagnosticreport', 'practitioner', 'performer'),
        ('diagnosticreport', 'practitionerrole', 'performer'),
        ('diagnosticreport', 'specimen', 'specimen'),
        ('encounter', 'location', 'location'),
        ('encounter', 'organization', 'serviceProvider'),
        ('encounter', 'patient', 'subject'),
        ('encounter', 'practitioner', 'participant'),
        ('goal', 'condition', 'addresses'),
        ('goal', 'patient', 'subject'),
        ('immunization', 'patient', 'patient'),
        ('immunization', 'practitioner', 'performer'),
        ('immunization', 'organization', 'manufacturer'),
        ('medicationrequest', 'medication', 'medicationReference'),
        ('medicationrequest', 'patient', 'subject'),
        ('medicationrequest', 'practitioner', 'requester'),
        ('observation', 'device', 'device'),
        ('observation', 'patient', 'subject'),
        ('observation', 'practitioner', 'performer'),
        ('observation', 'specimen', 'specimen'),
        ('procedure', 'device', 'usedReference'),
        ('procedure', 'location', 'location'),
        ('procedure', 'patient', 'subject'),
        ('procedure', 'practitioner', 'performer'),
    ]
    
    resource_counts = {}
    for resourceName, resource in created_resources.items():
        resourceType = resource['resourceType'].lower().strip()
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
        if sourceType in resource_counts and destinationType in resource_counts and \
        resource_counts[sourceType]['count'] == 1 and resource_counts[destinationType]['count'] == 1:
            originResourceEntityName = resource_counts[sourceType]['singletonEntityName']
            destinationResourceEntityName = resource_counts[destinationType]['singletonEntityName']
            resource_link_entities.append(
                ResourceLink(originResourceEntityName,fieldName,destinationResourceEntityName)
            )
    return
        
            
#List function to create resource references/links with created entities
def create_resource_links(created_resources, resource_link_entites, preview_mode = False):
    #TODO: Build resource links
    print("Building resource links")
    for resource_link_entity in resource_link_entites:
        create_resource_link(created_resources, resource_link_entity, preview_mode)
    return
    
#Singular function to create a resource link.
def create_resource_link(created_resources, resource_link_entity, preview_mode = False):
    # template scaffolding
    reference_json_block = {
        "reference" : "$value"
    }
    #Special reference handling blocks, in the form of (originResource, destinationResource, referencePath)
    arrayType_references = [
        ('diagnosticreport', 'specimen', 'specimen'),
        ('diagnosticreport', 'practitioner', 'performer'),
        ('diagnosticreport', 'practitionerrole', 'performer'),
        ('diagnosticreport', 'organization', 'performer'),
        ('diagnosticreport', 'careteam', 'performer'),
        ('diagnosticreport', 'observation', 'result'),
        ('diagnosticreport', 'imagingStudy', 'imagingStudy'),
    ]
    #Find the origin and destination resource from the link
    try:
        originResource = created_resources[resource_link_entity.originResource]
    except KeyError:
        print(f"WARNING: In ResourceLinks tab, found a Origin Resource of : {resource_link_entity.originResource}  but no such entity found in PatientData")
        return
    try:
        destinationResource = created_resources[resource_link_entity.destinationResource]
    except KeyError:
        print(f"WARNING: In ResourceLinks tab, found a Desitnation Resource  of : {resource_link_entity.destinationResource}  but no such entity found in PatientData")
        return
    #Estable the value of the refence
    if preview_mode:
        reference_value = destinationResource['resourceType'] + "/" + resource_link_entity.destinationResource
    else:
        reference_value = destinationResource['resourceType'] + "/" + destinationResource['id']
    link_tuple = (originResource['resourceType'].strip().lower(),
                    destinationResource['resourceType'].strip().lower(),
                    resource_link_entity.referencePath.strip().lower())
    if link_tuple in arrayType_references:
        if resource_link_entity.referencePath.strip().lower() not in originResource:
            originResource[resource_link_entity.referencePath.strip().lower()] = []
        new_reference = reference_json_block.copy()
        new_reference['reference'] = reference_value
        originResource[resource_link_entity.referencePath.strip().lower()].append(new_reference)
    else:
        originResource[resource_link_entity.referencePath.strip().lower()] = reference_json_block.copy()
        originResource[resource_link_entity.referencePath.strip().lower()]["reference"] = reference_value
    return

def add_resource_to_transaction_bundle(root_bundle, fhir_resource):
    entry = {}
    entry['fullUrl'] = "urn:uuid:"+fhir_resource['id']
    entry['resource'] = fhir_resource
    entry['request'] = {
      "method": "PUT",
      "url": fhir_resource['resourceType'] + "/" + fhir_resource['id']
    }
    root_bundle['entry'].append(entry)
    return root_bundle

#Drill down and create a structure from a json path with a simple recurisve process
# Supports 2 major features:
# 1) dot notation such as $.codeableconcept.coding[0].value = 1234
# 2) simple qualifiers such as $.name[use=official].family = Dickerson
# rootStruct: top level structure to drill into
# json_path: dotnotation path to follow
# resource_definition: resource description model from import
# entity_definition: specific field entry information for this function
# value: Actual value to assign
def create_structure_from_jsonpath(root_struct: Dict, json_path: str, resource_definition: ResourceDefinition,  dataType: str, value: Any):
    #Get all dot notation components as seperate 
    if dataType is not None and dataType.strip().lower() == 'string':
        value = str(value)
    
    if value == None:
        print(f"WARNING: Full jsonpath: {json_path} - Expected to find a value but found None instead")
        return root_struct
    #Start of top-level function which calls the enclosed recursive function
    parts = json_path.split('.')
    return build_structure(root_struct, json_path, resource_definition, dataType, parts, value, [])

# main recursive function to drill into the json structure, assign paths, and create structure where needed
def build_structure(current_struct: Any, json_path: str, resource_definition: ResourceDefinition, dataType: str, parts: List[str], value: Any, previous_parts: List[str]):
    if len(parts) == 0:
        return current_struct
    #Grab current part
    part = parts[0]
    #SPECIAL HANDLING CLAUSE
    matching_handler = next((handler for handler in special_values.custom_handlers if (json_path.startswith(handler) or json_path == handler)), None)
    if matching_handler is not None:
        return special_values.custom_handlers[matching_handler].assign_value(json_path, resource_definition, dataType,  current_struct, parts[-1], value)
    #Ignore dollar sign ($) and drill farther down
    if part == '$' or part == resource_definition.resourceType.strip():
        #Ignore the dollar sign and the resourcetype
        return build_structure_recurse(current_struct, json_path, resource_definition, dataType, parts, value, previous_parts, part)
    
    # If parts length is one then this is the final key to access and pair
    if len(parts) == 1:
        #Check for numeic qualifier '[0]' and '[1]'
        if '[' in part and ']' in part:
        #Seperate the key from the qualifier
            key_part = part[:part.index('[')]
            qualifier = part[part.index('[')+1:part.index(']')]
            qualifier_condition = qualifier.split('=')
            
            #If there is no key part, aka '[0]', '[1]' etc, then it's a simple accessor
            if key_part is None or key_part == '':
                if not qualifier.isdigit():
                    raise TypeError(f"ERROR: Full jsonpath: {json_path} - current path - {'.'.join(previous_parts + parts[:1])} - qualifier - {qualifier} - standalone qualifier expected to be a single index numeric ([0], [1], etc)")
                if current_struct == {}:
                    current_struct = []
                if not isinstance(current_struct, list):
                    raise TypeError(f"ERROR: Full jsonpath: {json_path} - current path - {'.'.join(previous_parts + parts[:1])} - Expected a list, but got {type(current_struct).__name__} instead.")
                part = int(qualifier)
                if part + 1 > len(current_struct):
                    current_struct.extend({} for x in range (part + 1 - len(current_struct)))
        #Actual assigning to the path
        fhir_formatting.assign_value(current_struct, part, value, dataType)
        return current_struct
    
    # If there is a simple qualifier with '['and ']'
    elif '[' in part and ']' in part:
        #Seperate the key from the qualifier
        key_part = part[:part.index('[')]
        qualifier = part[part.index('[')+1:part.index(']')]
        qualifier_condition = qualifier.split('=')
        
        #If there is no key part, aka '[0]', '[1]' etc, then it's a simple accessor
        if key_part is None or key_part == '':
            if not qualifier.isdigit():
                raise TypeError(f"ERROR: Full jsonpath: {json_path} - current path - {'.'.join(previous_parts + parts[:1])} - qualifier - {qualifier} - standalone qualifier expected to be a single index numeric ([0], [1], etc)")
            if current_struct == {}:
                current_struct = []
            if not isinstance(current_struct, list):
                raise TypeError(f"ERROR: Full jsonpath: {json_path} - current path - {'.'.join(previous_parts + parts[:1])} - Expected a list, but got {type(current_struct).__name__} instead.")
            qualifier_as_number = int(qualifier)
            if qualifier_as_number + 1 > len(current_struct):
                current_struct.extend({} for x in range (qualifier_as_number + 1 - len(current_struct)))
            inner_struct = current_struct[qualifier_as_number]
            inner_struct = build_structure_recurse(inner_struct, json_path, resource_definition, dataType, parts, value, previous_parts, part)
            current_struct[qualifier_as_number] = inner_struct
            return current_struct
        # Create the key part in the structure
        if (not key_part in current_struct) or (isinstance(current_struct[key_part], dict)):
            current_struct[key_part] = []
        #If there is a key_part and the If the qualifier condition is defined
        if len(qualifier_condition) == 2:
            #special handling for code
            if key_part != "coding" and (qualifier_condition[0] in ('code', 'system')):
                #Move into the coding section if a qualifier asks for 'code' or 'system'
                if 'coding' not in current_struct:
                    current_struct['coding'] = []
                    current_struct = current_struct['coding']
            qualifier_key, qualifier_value = qualifier_condition
            # Retrieve an inner structure if it exists allready that matches the criteria
            inner_struct = next((innerElement for innerElement in current_struct[key_part] if isinstance(innerElement, dict) and innerElement.get(qualifier_key) == qualifier_value), None)
            #If no inner structure exists, create one instead
            if inner_struct is None:
                inner_struct = {qualifier_key: qualifier_value}
                current_struct[key_part].append(inner_struct)
            #Recurse into that innerstructure where the qualifier matched to continue the part traversal
            inner_struct = build_structure_recurse(inner_struct, json_path, resource_definition, dataType, parts, value, previous_parts, part)
            return current_struct
        #If there's no qualifier condition, but an index aka '[0]', '[1]' etc, then it's a simple accessor
        elif qualifier.isdigit():
            if not isinstance(current_struct[key_part], list):
                raise TypeError(f"ERROR: Full jsonpath: {json_path} - current path - {'.'.join(previous_parts + [parts[0]])} - Expected a list, but got {type(current_struct).__name__} instead.")
            qualifier_as_number = int(qualifier)
            if qualifier_as_number > len(current_struct):
                current_struct[key_part].extend({} for x in range (qualifier_as_number - len(current_struct)))
            inner_struct = current_struct[key_part][qualifier_as_number]
            inner_struct = build_structure_recurse(inner_struct, json_path, resource_definition, dataType, parts, value, previous_parts, part)
            current_struct[key_part][qualifier_as_number] = inner_struct
            return current_struct
    #None qualifier accessor
    else:
        if(part not in current_struct):
            current_struct[part] = {}
        inner_struct = build_structure_recurse(current_struct[part], json_path, resource_definition, dataType, parts, value, previous_parts, part)
        current_struct[part] = inner_struct
        return current_struct
    
#Helper function to quickly recurse and return the next level of structure. Used by main recursive function
def build_structure_recurse(current_struct, json_path, resource_definition, dataType, parts, value, previous_parts, part):
    previous_parts.append(part)
    return_struct = build_structure(current_struct, json_path, resource_definition, dataType, parts[1:], value, previous_parts)
    return return_struct

#Post-process function to add medication reference in specific references
def post_process_create_medication_references( root_bundle: dict):
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

def createMedicationResource(root_bundle, medicationCodeableConcept):
    target_medication = initialize_resource(ResourceDefinition.from_dict({'ResourceType': 'Medication'}))
    target_medication['code'] = medicationCodeableConcept
    add_resource_to_transaction_bundle(root_bundle, target_medication)
    return target_medication