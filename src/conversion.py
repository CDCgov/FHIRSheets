import uuid
from jsonpath_ng.jsonpath import Fields, Slice, Where
from jsonpath_ng.ext import parse as parse_ext

#Creates a full transaction bundle for a patient at index
def create_transaction_bundle(resource_definition_entities, resource_link_entities, patient_data, index = 0):
    root_bundle = initialize_bundle()
    created_resources = {}
    for resource_definition in resource_definition_entities:
        entity_name = resource_definition['Entity Name']
        #Create and collect fhir resources
        fhir_resource = create_fhir_resource(resource_definition, patient_data, index)
        created_resources[entity_name] = fhir_resource
    #Link resources after creation
    create_resource_links(created_resources, resource_link_entities)
    #Construct into fhir bundle
    for fhir_resource in created_resources.values():
        add_resource_to_transaction_bundle(root_bundle, fhir_resource)
    return root_bundle

#Initialize root bundle definition
def initialize_bundle():
    root_bundle = {}
    root_bundle['resourceType'] = 'Bundle'
    root_bundle['id'] = str(uuid.uuid4())
    root_bundle['type'] = 'transaction'
    root_bundle['entry'] = []
    return root_bundle

# Creates a fhir-json structure from a resource definition entity and the patient_data_sheet
def create_fhir_resource(resource_definition, patient_data, index = 0):
    resource_dict = initialize_resource(resource_definition)
    #Get field entries for this entitiy
    try:
        all_field_entries = patient_data[resource_definition['Entity Name']]
    except KeyError:
        print(f"Patient index {index} - Create Fhir Resource Error - {resource_definition['Entity Name']} - No columns found for resource in 'PatientData' sheet")
        return resource_dict
    #For each field within the entity
    for field_entry in all_field_entries.values():
        #Create a jsonpath from each provided json path and value for this resource
        if field_entry['values'] and len(field_entry['values']) > index:
            create_structure_from_jsonpath(resource_dict, field_entry['jsonpath'], resource_definition, field_entry['values'][index])
    return resource_dict
        
#Initialize a resource from a resource definition. Adding basic 
def initialize_resource(resource_definition):
    initial_resource = {}
    initial_resource['resourceType'] = resource_definition['ResourceType']
    resource_definition['id'] = str(uuid.uuid4())
    initial_resource['id'] = resource_definition['id']
    if resource_definition['Profile(s)']:
        initial_resource['meta'] = {
            'profile': resource_definition['Profile(s)']
        }
    return initial_resource

#Create resource references/links with created entities
def create_resource_links(created_resources, resource_link_entites):
    #TODO: Build resource links
    return
    
def add_resource_to_transaction_bundle(root_bundle, fhir_resource):
    entry = {}
    entry['fullUrl'] = "urn:uuid"+fhir_resource['id']
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
# json_path: dotnotation path to    
def create_structure_from_jsonpath(root_struct, json_path, resource_definition, value):
    #Get all dot notation components as seperate 
    parts = json_path.split('.')
    #Recursive function to drill into 
    def _build_structure(current_struct, parts, value, previous_parts):
        if len(parts) == 0:
            return current_struct
        #Grab current part
        part = parts[0]
        #Ignore dollar sign ($) and drill farther down
        if part == '$' or part == resource_definition['ResourceType']:
            _build_structure(current_struct, parts[1:], value, previous_parts.append(part))
            return current_struct
        
        # If parts length is one then this is the final key to access and pair
        if len(parts) == 1:
            #Actual assigning to the path
            current_struct[part] = value
            return current_struct
        # If there is a simple qualifier with '['and ']'
        elif '[' in part and ']' in part:
            #Seperate the key from the qualifier
            key_part = part[:part.index('[')]
            qualifier = part[part.index('[')+1:part.index(']')]
            qualifier_condition = qualifier.split('=')
            #If there is no key part, aka '[0]', '[1]' etc, then it's a simple accessor
            if key_part is None or key_part is '':
                if current_struct is None:
                    current_struct = []
                if not qualifier.isdigit():
                    raise TypeError(f"Full jsonpath: {json_path} - current path - {'.'.join(previous_parts + parts[0])} - qualifier - {qualifier} - standalone qualifier expected to be a single index numeric ([0], [1], etc)")
                if not isinstance(current_struct, list):
                    raise TypeError(f"Full jsonpath: {json_path} - current path - {'.'.join(previous_parts + parts[0])} - Expected a list, but got {type(current_struct).__name__} instead.")
                qualifier_as_number = int(qualifier)
                if qualifier_as_number > len(current_struct):
                    current_struct.extend({} for x in range (qualifier_as_number - len(current_struct)))
                inner_struct = current_struct[qualifier_as_number]
                _build_structure(inner_struct, parts[1:], value, previous_parts.append(part))
                return current_struct
            
            #If the qualifier condition is defined
            # Re-assign the current struct key to an array if it was a dictionary
            if current_struct[key_part] is None or current_struct[key_part] == {}:
                current_struct[key_part] == []
            if len(qualifier_condition) == 2:
                qualifier_key, qualifier_value = qualifier_condition
                # Retrieve an inner structure if it exists allready that matches the criteria
                inner_struct = next((innerElement for innerElement in current_struct if innerElement.get(qualifier_key) == qualifier_value))
                #If no inner structure exists, create one instead
                if inner_struct is None:
                    inner_struct = {qualifier_key: qualifier_value}
                    current_struct[key_part].append(inner_struct)
                #Recurse into that innerstructure where the qualifier matched to continue the part traversal
                _build_structure(inner_struct, parts[1:], value, previous_parts.append(part))
                return current_struct
            #If there's no qualifier condition, but an index aka '[0]', '[1]' etc, then it's a simple accessor
            elif qualifier.isdigit():
                if current_struct is None:
                    current_struct = []
                if not isinstance(current_struct, list):
                    raise TypeError(f"Full jsonpath: {json_path} - current path - {'.'.join(previous_parts + parts[0])} - Expected a list, but got {type(current_struct).__name__} instead.")
                qualifier_as_number = int(qualifier)
                if qualifier_as_number > len(current_struct):
                    current_struct.extend({} for x in range (qualifier_as_number - len(current_struct)))
                inner_struct = current_struct[qualifier_as_number]
                _build_structure(inner_struct, parts[1:], value, previous_parts.append(part))
                return current_struct
        #If this is simply a drill down to a lower key level
        else:
            current_struct[part] = {}
            _build_structure(current_struct[part], parts[1:], value, previous_parts.append(part))
            return current_struct

    #Real call to the recursive function from the root structure to drill
    return _build_structure(root_struct, json_path, value, [])