import argparse
import read_input
import conversion
from pathlib import Path

def main(input_file, output_folder):
    # Step 1: Read the input file using read_input module
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    data = read_input.read_xlsx_and_process(input_file)
    resource_definition_entities = data['resource_definition_entities']
    
    #For each index of patients
    for i in range(0,data['num_entries']):
        # Construct the file path for each JSON file
        file_path = Path(output_folder) / f"{i}.json"
        #Create a bundle
        fhir_bundle = conversion.create_transaction_bundle(data['resource_definition_entities'],
                                                        data['resource_link_entites'], data['patient_data'], i)
        # Step 3: Write the processed data to the output file
        with open(file_path, 'w') as json_file:
            json.dump(fhir_bundle, json_file, indent=4)

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