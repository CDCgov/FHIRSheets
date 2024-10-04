import argparse
import read_input
import conversion
import orjson
from pathlib import Path

def main(input_file, output_folder):
    # Step 1: Read the input file using read_input module
    
    # Check if the output folder exists, and create it if not
    
    output_folder_path = Path(output_folder)
    if not output_folder_path.is_absolute():
        output_folder_path = Path().cwd() / Path(output_folder)
    if not output_folder_path.exists():
        output_folder_path.mkdir(parents=True, exist_ok=True)  # Create the folder if it doesn't exist
    data = read_input.read_xlsx_and_process(input_file)
    resource_definition_entities = data['resource_definition_entities']
    
    #For each index of patients
    for i in range(0,data['num_entries']):
        # Construct the file path for each JSON file
        file_path = output_folder_path / f"{i}.json"
        #Create a bundle
        fhir_bundle = conversion.create_transaction_bundle(data['resource_definition_entities'],
                                                        data['resource_link_entities'], data['patient_data_entities'], i)
        # Step 3: Write the processed data to the output file
        json_string = orjson.dumps(fhir_bundle)
        with open(file_path, 'wb') as json_file:
            json_file.write(json_string)

if __name__ == "__main__":
    # Create the argparse CLI
    parser = argparse.ArgumentParser(description="Process input, convert data, and write output.")
    
    # Define the input file argument
    parser.add_argument('--input_file', type=str, help="Path to the input xlsx ", default="resources/Synthetic_Input_Baseline.xlsx")
    
    # Define the output file argument
    parser.add_argument('--output_folder', type=str, help="Path to save the output files", default="output/")
    
    # Parse the arguments
    args = parser.parse_args()

    # Call the main function with the provided arguments
    main(args.input_file, args.output_folder)