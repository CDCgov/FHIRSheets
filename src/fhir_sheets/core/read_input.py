import openpyxl

from .model.cohort_data_entity import CohortData, CohortData

from .model.resource_definition_entity import ResourceDefinition
from .model.resource_link_entity import ResourceLink

# Function to read the xlsx file and access specific sheets
def read_xlsx_and_process(file_path):
    # Load the workbook
    workbook = openpyxl.load_workbook(file_path)

    # Example of accessing specific sheets
    if 'ResourceDefinitions' in workbook.sheetnames:
        sheet = workbook['ResourceDefinitions']
        resource_definition_entities = process_sheet_resource_definitions(sheet)

    if 'ResourceLinks' in workbook.sheetnames:
        sheet = workbook['ResourceLinks']
        resource_link_entities = process_sheet_resource_links(sheet)

    if 'PatientData' in workbook.sheetnames:
        sheet = workbook['PatientData']
        cohort_data = process_sheet_patient_data_revised(sheet, resource_definition_entities)
    
    return resource_definition_entities, resource_link_entities, cohort_data


# Function to process the specific sheet with 'Entity Name', 'ResourceType', and 'Profile(s)'
def process_sheet_resource_definitions(sheet):
    resource_definitions = []
    resource_definition_entities = []
    headers = [cell.value for cell in next(sheet.iter_rows(min_row=1, max_row=1))]  # Get headers

    for row in sheet.iter_rows(min_row=3, values_only=True):
        row_data = dict(zip(headers, row))  # Create a dictionary for each row
        if all(cell is None or cell == "" for cell in row_data.values()):
            continue
        # Split 'Profile(s)' column into a list of URLs
        if row_data.get("Profile(s)"):
            row_data["Profile(s)"] = [url.strip() for url in row_data["Profile(s)"].split(",")]
        resource_definition_entities.append(ResourceDefinition(row_data))
        resource_definitions.append(row_data)

    return resource_definition_entities

# Function to process the specific sheet with 'OriginResource', 'ReferencePath', and 'DestinationResource'
def process_sheet_resource_links(sheet):
    resource_links = []
    resource_link_entities = []
    headers = [cell.value for cell in next(sheet.iter_rows(min_row=1, max_row=1))]  # Get headers
    for row in sheet.iter_rows(min_row=3, values_only=True):
        row_data = dict(zip(headers, row))  # Create a dictionary for each row
        if all(cell is None or cell == "" for cell in row_data):
            continue
        resource_links.append(row_data)
        resource_link_entities.append(ResourceLink(row_data))

    return resource_link_entities

# Function to process the "PatientData" sheet
def process_sheet_patient_data(sheet, resource_definition_entities):
    # Initialize the dictionary to store the processed data
    patient_data = {}
    cohort_data = CohortData()
    # Extract the data from the first 6 rows (Entity To Query, JsonPath, etc.)
    for col in sheet.iter_cols(min_row=1, max_row=6, min_col=3, values_only=True):  # Start from 3rd column
        if all(entry is None for entry in col):
            continue
        entity_name = col[0]  # The entity name comes from the first row (Entity To Query)
        field_name = col[5]  #The "Data Element" comes from the fifth row
        if (entity_name is None or entity_name == "") and (field_name is not None and field_name != ""):
            print(f"WARNING: - Reading Patient Data Issue - {field_name} - 'Entity To Query' cell missing for column labelled '{field_name}', please provide entity name from the ResourceDefinitions tab.")

        if entity_name not in [entry.entity_name for entry in resource_definition_entities]:
            print(f"WARNING: - Reading Patient Data Issue - {field_name} - 'Entity To Query' cell has entity named '{entity_name}', however, the ResourceDefinition tab has no matching resource. Please provide a corresponding entry in the ResourceDefinition tab.")
        # Create structure for this entity if not already present
        if entity_name not in patient_data:
            patient_data[entity_name] = {}
            cohort_data.insert_entity(entity_name, EntityData({}))

        # Add jsonpath, valuesets, and initialize an empty list for 'values'
        if field_name not in patient_data[entity_name]:
            field_data = {
                "jsonpath": col[1],  # JsonPath from the second row
                "valueType": col[2], # Value Type from the third row
                "valuesets": col[3], # Value Set from the fourth row
                "values": []         # Initialize empty list for actual values
            }
            patient_data[entity_name][field_name] = field_data
            cohort_data.entities[entity_name].insert(field_name, FieldEntry(field_data))
    
    # Now process the rows starting from the 6th row (the actual data entries)
    num_entries = 0
    for row in sheet.iter_rows(min_row=7, values_only=True):  # Start from row 6 for actual data
        if all(cell is None for cell in row):
            continue
        num_entries = num_entries + 1
        entity_name = row[0]  # The entity name comes from the first column of each row
        for i, value in enumerate(row[2:], start=1):  # Iterate through the values in the columns
            entity_name = sheet.cell(row=1, column=i + 2).value
            field_name = sheet.cell(row=6, column=i + 2).value  # Get the Data Element for this column
            if entity_name in patient_data and field_name in patient_data[entity_name]:
                # Append the actual data values to the 'values' array
                cohort_data.entities[entity_name].fields[field_name].values.append(value)
    cohort_data.num_entries = num_entries
    return cohort_data

# Function to process the "PatientData" sheet for the Revised CohortData
def process_sheet_patient_data_revised(sheet, resource_definition_entities):
    headers = []
    patients = []
    # Initialize the dictionary to store the processed data
    # Process the Header Entries from the first 6 rows (Entity To Query, JsonPath, etc.) and the data from the rest.
    for col in sheet.iter_cols(min_row=1, min_col=3, values_only=True):  # Start from 3rd column
        if all(entry is None for entry in col):
            continue
        entity_name = col[0]  # The entity name comes from the first row (Entity To Query)
        field_name = col[5]  #The "Data Element" comes from the fifth row
        if (entity_name is None or entity_name == "") and (field_name is not None and field_name != ""):
            print(f"WARNING: - Reading Patient Data Issue - {field_name} - 'Entity To Query' cell missing for column labelled '{field_name}', please provide entity name from the ResourceDefinitions tab.")

        if entity_name not in [entry.entity_name for entry in resource_definition_entities]:
            print(f"WARNING: - Reading Patient Data Issue - {field_name} - 'Entity To Query' cell has entity named '{entity_name}', however, the ResourceDefinition tab has no matching resource. Please provide a corresponding entry in the ResourceDefinition tab.")

        # Create a header entry
        header_data = {
            "fieldName": field_name,
            "entityName": entity_name,
            "jsonpath": col[1],  # JsonPath from the second row
            "valueType": col[2], # Value Type from the third row
            "valuesets": col[3] # Value Set from the fourth row
        }
        headers.append(header_data)
        # Create a data entry
        values = col[6:] # The values come from the 6th row and below
        values = tuple(item for item in values if item is not None)
        #Expand the patient dictionary set if needed
        if len(values) > len(patients):
            needed_count = len(values) - len(patients)
            patients.extend([{}] * needed_count)
        for patient_dict, value in zip(patients, values):
            patient_dict[(entity_name, field_name)] = value
    cohort_data = CohortData(headers=headers, patients=patients)
    return cohort_data