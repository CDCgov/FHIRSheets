from ..core import read_input
from ..core import conversion

import argparse
import orjson
import json
from pathlib import Path
from pprint import pprint

def find_sets(d, path=""):
    if isinstance(d, dict):
        for key, value in d.items():
            new_path = f"{path}.{key}" if path else str(key)
            find_sets(value, new_path)
    elif isinstance(d, list):  # Handle lists of dictionaries
        for idx, item in enumerate(d):
            find_sets(item, f"{path}[{idx}]")
    elif isinstance(d, set):
        print(f"Set found at path: {path}")
        
def main(input_file, output_folder):
    # Step 1: Read the input file using read_input module
    
    # Check if the output folder exists, and create it if not
    
    output_folder_path = Path(output_folder)
    if not output_folder_path.is_absolute():
        output_folder_path = Path().cwd() / Path(output_folder)
    if not output_folder_path.exists():
        output_folder_path.mkdir(parents=True, exist_ok=True)  # Create the folder if it doesn't exist
    resource_definition_entities, resource_link_entities, cohort_data = read_input.read_xlsx_and_process(input_file)
    pprint(cohort_data)
    #For each index of patients
    for i in range(0,cohort_data.get_num_patients()):
        # Construct the file path for each JSON file
        file_path = output_folder_path / f"{i}.json"
        #Create a bundle
        fhir_bundle = conversion.create_transaction_bundle(resource_definition_entities, resource_link_entities, cohort_data, i)
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
    
    # Parse the arguments
    args = parser.parse_args()

    # Call the main function with the provided arguments
    main(args.input_file, args.output_folder)