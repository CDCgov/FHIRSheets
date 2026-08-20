"""Excel input reading and processing module.

This module handles reading Excel files in the FHIR cohort format and converting
them into structured data models. It processes three main sheets:
    - ResourceDefinitions: Entity definitions with resource types and profiles
    - ResourceLinks: Reference relationships between resources
    - PatientData: Actual patient data with headers and values

Functions:
    read_xlsx_and_process: Main entry point for reading Excel files
    process_sheet_resource_definitions: Parse ResourceDefinitions sheet
    process_sheet_resource_links: Parse ResourceLinks sheet
    process_sheet_patient_data_revised: Parse PatientData sheet
"""

from typing import List
import openpyxl
from openpyxl.utils import get_column_letter
import logging

from .model.cohort_data_entity import CohortData, CohortData

from .model.resource_definition_entity import ResourceDefinition
from .model.resource_link_entity import ResourceLink

logger: logging.Logger = logging.getLogger("fhirsheets.core.read_input")

# Rows 1 through 6 of the PatientData tab are headers, read by position.
HEADER_ROW_COUNT = 6

def read_xlsx_and_process(file_path):
    """Read and process an Excel file in FHIR cohort format.
    
    This is the main entry point for reading Excel input. It loads the workbook
    and processes three sheets: ResourceDefinitions, ResourceLinks, and PatientData.
    
    Args:
        file_path: Path to the Excel file (.xlsx)
        
    Returns:
        Tuple of (resource_definitions, resource_links, cohort_data):
            - resource_definitions: List of ResourceDefinition objects
            - resource_links: List of ResourceLink objects
            - cohort_data: CohortData object with headers and patient entries
            
    Example:
        >>> defs, links, data = read_xlsx_and_process('input.xlsx')
        >>> print(len(defs))
        5
        >>> print(data.get_num_patients())
        10
    """
    # Load the workbook
    workbook = openpyxl.load_workbook(file_path)
    resource_definition_entities = []
    resource_link_entities = []
    cohort_data = CohortData.from_dict([],[])
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


def process_sheet_resource_definitions(sheet) -> List[ResourceDefinition]:
    """Process the ResourceDefinitions sheet into ResourceDefinition objects.
    
    Parses the ResourceDefinitions sheet which defines entities with their
    resource types and optional FHIR profiles. The sheet should have columns:
        - Entity Name: Unique identifier for the entity
        - ResourceType: FHIR resource type (e.g., 'Patient', 'Observation')
        - Profile(s): Comma-separated list of FHIR profile URLs (optional)
    
    Args:
        sheet: openpyxl worksheet object for ResourceDefinitions sheet
        
    Returns:
        List of ResourceDefinition objects
        
    Example:
        >>> definitions = process_sheet_resource_definitions(sheet)
        >>> print(definitions[0].entityName)
        'Patient'
        >>> print(definitions[0].resourceType)
        'Patient'
    """
    resource_definitions = []
    resource_definition_entities = []
    headers = [cell.value for cell in next(sheet.iter_rows(min_row=1, max_row=1))]  # Get headers

    for row in sheet.iter_rows(min_row=3, values_only=True):
        row_data = dict((h, r) for h, r in zip(headers, row) if h is not None)  # Create a dictionary for each row
        if all(cell is None or cell == "" for cell in row_data.values()):
            continue
        # Split 'Profile(s)' column into a list of URLs
        if row_data.get("Profile(s)"):
            row_data["Profile(s)"] = [url.strip() for url in row_data["Profile(s)"].split(",")]
        resource_definition_entities.append(ResourceDefinition.from_dict(row_data))
        resource_definitions.append(row_data)
    logger.info(f"Resource Definitions\n----------{resource_definitions}")
    return resource_definition_entities

def process_sheet_resource_links(sheet) -> List[ResourceLink]:
    """Process the ResourceLinks sheet into ResourceLink objects.
    
    Parses the ResourceLinks sheet which defines reference relationships between
    resources. The sheet should have columns:
        - OriginResource: Entity name of the source resource
        - ReferencePath: JSON path where the reference should be created
        - DestinationResource: Entity name of the target resource
    
    Args:
        sheet: openpyxl worksheet object for ResourceLinks sheet
        
    Returns:
        List of ResourceLink objects
        
    Example:
        >>> links = process_sheet_resource_links(sheet)
        >>> print(links[0].originResource)
        'Observation'
        >>> print(links[0].referencePath)
        'subject'
        >>> print(links[0].destinationResource)
        'Patient'
    """
    resource_links = []
    resource_link_entities = []
    headers = [cell.value for cell in next(sheet.iter_rows(min_row=1, max_row=1))]  # Get headers
    for row in sheet.iter_rows(min_row=3, values_only=True):
        row_data = dict(zip(headers, row))  # Create a dictionary for each row
        if all(cell is None or cell == "" for cell in row_data):
            continue
        resource_links.append(row_data)
        resource_link_entities.append(ResourceLink.from_dict(row_data))
    logger.info(f"Resource Links\n----------{resource_links}")
    return resource_link_entities

def process_sheet_patient_data_revised(sheet, resource_definition_entities):
    """Process the PatientData sheet into CohortData object.
    
    Parses the PatientData sheet which contains field definitions in the first
    6 rows and patient data in subsequent rows. The sheet structure:
        Row 1: Entity To Query (entity name)
        Row 2: JsonPath (path in FHIR resource)
        Row 3: Value Type (FHIR data type)
        Row 4: Value Set (FHIR value set URL)
        Row 5: (unused)
        Row 6: Data Element (field name)
        Row 7+: Patient data values
    
    Args:
        sheet: openpyxl worksheet object for PatientData sheet
        resource_definition_entities: List of ResourceDefinition objects for validation
        
    Returns:
        CohortData object containing headers and patient entries
        
    Example:
        >>> cohort = process_sheet_patient_data_revised(sheet, definitions)
        >>> print(cohort.get_num_patients())
        10
        >>> print(len(cohort.headers))
        25
    """
    headers = []
    patients = []
    # Initialize the dictionary to store the processed data
    # Process the Header Entries from the first 6 rows (Entity To Query, JsonPath, etc.) and the data from the rest.
    for column_index, col in enumerate(sheet.iter_cols(min_row=1, min_col=3, values_only=True), start=3):  # Start from 3rd column
        if all(entry is None for entry in col):
            continue
        # The header rows are read by position, so a sheet that stops before
        # row 6 gives a column too short to index. Pad it out and let the
        # checks below report what is missing.
        if len(col) < HEADER_ROW_COUNT:
            column_label = get_column_letter(column_index)
            logger.warning(f"Reading Patient Data Issue - column {column_label} - only {len(col)} of the {HEADER_ROW_COUNT} header rows are present, please fill in the header rows on the PatientData tab.")
            col = col + (None,) * (HEADER_ROW_COUNT - len(col))
        entity_name = col[0]  # The entity name comes from the first row (Entity To Query)
        field_name = col[5]  #The "Data Element" comes from the fifth row
        if (entity_name is None or entity_name == "") and (field_name is not None and field_name != ""):
            logger.warning(f"Reading Patient Data Issue - {field_name} - 'Entity To Query' cell missing for column labelled '{field_name}', please provide entity name from the ResourceDefinitions tab.")

        if entity_name not in [entry.entityName for entry in resource_definition_entities]:
            logger.warning(f"Reading Patient Data Issue - {field_name} - 'Entity To Query' cell has entity named '{entity_name}', however, the ResourceDefinition tab has no matching resource. Please provide a corresponding entry in the ResourceDefinition tab.")

        # Create a header entry
        header_data = {
            "fieldName": field_name,
            "entityName": entity_name,
            "jsonPath": col[1],  # JsonPath from the second row
            "valueType": col[2], # Value Type from the third row
            "valueSets": col[3] # Value Set from the fourth row
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
    logger.info(f"Headers\n----------{headers}")
    logger.info(f"Patients\n----------{patients}")
    cohort_data = CohortData.from_dict(headers=headers, patients=patients)
    return cohort_data