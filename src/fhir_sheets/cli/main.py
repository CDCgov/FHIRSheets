from ..core.config.FhirSheetsConfiguration import FhirSheetsConfiguration
from ..core import read_input
from ..core import conversion

import logging
import argparse
import orjson
import json
from pathlib import Path

logger: logging.Logger = logging.getLogger("fhirsheets.cli.main")

def find_sets(d, path=""):
    if isinstance(d, dict):
        for key, value in d.items():
            new_path = f"{path}.{key}" if path else str(key)
            find_sets(value, new_path)
    elif isinstance(d, list):  # Handle lists of dictionaries
        for idx, item in enumerate(d):
            find_sets(item, f"{path}[{idx}]")
    elif isinstance(d, set):
        logger.info(f"Set found at path: {path}")
        
def main(input_file, output_folder, config=FhirSheetsConfiguration({})):
    # Step 1: Read the input file using read_input module
    
    # Check if the output folder exists, and create it if not
    
    output_folder_path = Path(output_folder)
    if not output_folder_path.is_absolute():
        output_folder_path = Path().cwd() / Path(output_folder)
    if not output_folder_path.exists():
        output_folder_path.mkdir(parents=True, exist_ok=True)  # Create the folder if it doesn't exist
    resource_definition_entities, resource_link_entities, cohort_data = read_input.read_xlsx_and_process(input_file)
    #For each index of patients
    for i in range(0,cohort_data.get_num_patients()):
        # Construct the file path for each JSON file
        file_path = output_folder_path / f"{i}.json"
        #Create a bundle
        fhir_bundle = conversion.create_transaction_bundle(resource_definition_entities, resource_link_entities, cohort_data, i, config)
        # Step 3: Write the processed data to the output file
        find_sets(fhir_bundle)
        json_string = orjson.dumps(fhir_bundle)
        with open(file_path, 'wb') as json_file:
            json_file.write(json_string)
        with open(file_path, 'r') as json_file:
            json_string = json.load(json_file)
        with open(file_path, 'w') as json_file:
            json.dump(json_string, json_file, indent = 4)

if __name__ == "__main__":
    # Create the argparse CLI
    parser = argparse.ArgumentParser(description="Process input, convert data, and write output.")
    
    # Define the input file argument
    parser.add_argument('--input_file', type=str, help="Path to the input xlsx ", default="src/resources/Synthetic_Input_Baseline.xlsx")
    
    # Define the output file argument
    parser.add_argument('--output_folder', type=str, help="Path to save the output files", default="output/")
    
    # Config file argument
    parser.add_argument('--config_file', type=str, help="Path to a JSON configuration file. If provided, this will be used instead of individual config arguments.", default=None)
    
    # Config object arguments (used if --config_file is not provided)
    parser.add_argument('--preview_mode', type=str, help="Configuration option to generate resources as 'preview mode' references will reference the entity name. Will primarily be used to render a singular resource for preview.", default=False)
    
    parser.add_argument('--medications_as_reference', type=str, help="Configuration option to create medication references. You may still provide medicationCodeableConcept, but a post process will convert the codeableconcepts to medication resources", default=False)
    
    parser.add_argument('--build_empty_resources', type=str, help="Configuration option to build resources even when no data entries exist for that entity.", default=False)
    
    parser.add_argument('--enable_default_resource_links', type=str, help="Configuration option to enable/disable automatic default resource linking.", default=True)
    
    # Flag to disable default resource links (overrides --enable_default_resource_links)
    parser.add_argument('--no-default-links', action='store_true', help="Disable automatic default resource linking (shorthand for --enable_default_resource_links false)")
    
    # Parse the arguments
    args = parser.parse_args()

    # Load configuration
    if args.config_file:
        # Load configuration from JSON file
        config_path = Path(args.config_file)
        if not config_path.exists():
            logger.error(f"Configuration file not found: {args.config_file}")
            exit(1)
        try:
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
            config = FhirSheetsConfiguration(config_dict)
            logger.info(f"Loaded configuration from {args.config_file}")
        except Exception as e:
            logger.error(f"Error loading configuration file: {e}")
            exit(1)
    else:
        # Use command-line arguments
        config_dict = vars(args)
        # Handle the --no-default-links flag
        if args.no_default_links:
            config_dict['enable_default_resource_links'] = False
        config = FhirSheetsConfiguration(config_dict)
    
    # Call the main function with the provided arguments
    main(args.input_file, args.output_folder, config)
