"""Command-line interface for FHIRSheets.

This module provides the CLI entry point for converting Excel files in FHIR
cohort format to FHIR bundle JSON files. It handles argument parsing,
configuration loading, and output formatting.

Functions:
    main: Core conversion logic
    write_bundles: Write transaction bundles (one per patient)
    write_ndjson: Write NDJSON files organized by resource type
    cli: Console script entry point
    find_sets: Debug utility to find set objects in data structures
"""

from ..core.config.FhirSheetsConfiguration import FhirSheetsConfiguration
from ..core import read_input
from ..core import conversion

import logging
import argparse
import orjson
import json
from pathlib import Path
from collections import defaultdict

logger: logging.Logger = logging.getLogger("fhirsheets.cli.main")

def find_sets(d, path=""):
    """Debug utility to recursively find set objects in data structures.
    
    Args:
        d: Data structure to search (dict, list, or other)
        path: Current path in the structure (for logging)
    """
    if isinstance(d, dict):
        for key, value in d.items():
            new_path = f"{path}.{key}" if path else str(key)
            find_sets(value, new_path)
    elif isinstance(d, list):  # Handle lists of dictionaries
        for idx, item in enumerate(d):
            find_sets(item, f"{path}[{idx}]")
    elif isinstance(d, set):
        logger.info(f"Set found at path: {path}")

def write_bundles(bundles, output_folder_path):
    """Write transaction bundles to individual JSON files (one per patient).
    
    Each bundle is written to a file named {index}.json with pretty-printed
    formatting for readability.
    
    Args:
        bundles: List of FHIR Bundle dictionaries
        output_folder_path: Path object for output directory
    """
    for i, fhir_bundle in enumerate(bundles):
        file_path = output_folder_path / f"{i}.json"
        find_sets(fhir_bundle)
        json_string = orjson.dumps(fhir_bundle)
        with open(file_path, 'wb') as json_file:
            json_file.write(json_string)
        with open(file_path, 'r') as json_file:
            json_string = json.load(json_file)
        with open(file_path, 'w') as json_file:
            json.dump(json_string, json_file, indent = 4)
        logger.info(f"Wrote bundle {i} to {file_path}")

def write_ndjson(bundles, output_folder_path):
    """Write NDJSON files organized by resource type.
    
    Extracts all resources from bundles and writes them to separate NDJSON
    files based on resource type (e.g., Patient.ndjson, Observation.ndjson).
    Each line in the NDJSON file is a complete JSON object.
    
    Args:
        bundles: List of FHIR Bundle dictionaries
        output_folder_path: Path object for output directory
    """
    # Collect resources by type
    resources_by_type = defaultdict(list)
    
    for bundle in bundles:
        if "entry" in bundle:
            for entry in bundle["entry"]:
                if "resource" in entry:
                    resource = entry["resource"]
                    resource_type = resource.get("resourceType")
                    
                    if resource_type:
                        resources_by_type[resource_type].append(resource)
    
    # Write each resource type to its own NDJSON file
    for resource_type, resources in resources_by_type.items():
        output_path = output_folder_path / f"{resource_type}.ndjson"
        with open(output_path, "wb") as f:
            for resource in resources:
                # Write each resource as a single line of JSON (no indentation)
                json_line = orjson.dumps(resource)
                f.write(json_line + b"\n")
        
        logger.info(f"Wrote {len(resources)} {resource_type} resources to {output_path}")
        
def main(input_file, output_folder, format='bundle', config=FhirSheetsConfiguration({})):
    """Main conversion function for processing Excel to FHIR bundles.
    
    Reads an Excel file in FHIR cohort format, converts each patient row to
    a FHIR bundle, and writes output in the specified format.
    
    Args:
        input_file: Path to input Excel file (.xlsx)
        output_folder: Path to output directory
        format: Output format - 'bundle' for transaction bundles or 'ndjson'
                for newline-delimited JSON (default: 'bundle')
        config: FhirSheetsConfiguration object controlling conversion behavior
        
    Example:
        >>> config = FhirSheetsConfiguration({'preview_mode': False})
        >>> main('input.xlsx', 'output/', 'bundle', config)
    """
    # Step 1: Read the input file using read_input module
    
    # Check if the output folder exists, and create it if not
    
    output_folder_path = Path(output_folder)
    if not output_folder_path.is_absolute():
        output_folder_path = Path().cwd() / Path(output_folder)
    if not output_folder_path.exists():
        output_folder_path.mkdir(parents=True, exist_ok=True)  # Create the folder if it doesn't exist
    resource_definition_entities, resource_link_entities, cohort_data = read_input.read_xlsx_and_process(input_file)
    
    # Create bundles for all patients
    bundles = []
    for i in range(0, cohort_data.get_num_patients()):
        fhir_bundle = conversion.create_transaction_bundle(resource_definition_entities, resource_link_entities, cohort_data, i, config)
        bundles.append(fhir_bundle)
    
    # Write output based on format
    if format.lower() == 'ndjson':
        write_ndjson(bundles, output_folder_path)
    else:
        write_bundles(bundles, output_folder_path)

def cli():
    """Console script entry point for fhir-sheets command.
    
    Parses command-line arguments, loads configuration, and invokes the main
    conversion function. This is the entry point defined in pyproject.toml
    for the 'fhir-sheets' command.
    
    Command-line arguments:
        --input_file: Path to input Excel file
        --output_folder: Path to output directory
        --format: Output format ('bundle' or 'ndjson')
        --config_file: Path to JSON configuration file
        --preview_mode: Enable preview mode
        --medications_as_reference: Convert medications to references
        --build_empty_resources: Build resources even with no data
        --enable_default_resource_links: Enable automatic reference linking
        --no-default-links: Disable automatic reference linking (shorthand)
        --ai-mode: Enable AI-powered interactive mode for FHIR resource generation
    """
    # Create the argparse CLI
    parser = argparse.ArgumentParser(
        description="Process input, convert data, and write output.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # AI Mode arguments group
    ai_group = parser.add_argument_group('AI Mode Options', 'Options for AI-powered interactive and batch processing modes')
    ai_group.add_argument('--ai_mode', action='store_true', 
                         help="Enable AI-powered interactive mode for FHIR resource generation")
    ai_group.add_argument('--ai_mode_output_folder', type=str, 
                         help="[AI Mode] Path to save the output files (default: output_ai/)", 
                         default="output_ai/")
    
    # Batch Mode arguments group (subset of AI mode)
    batch_group = parser.add_argument_group('Batch Processing Options', 
                                           'Options for automated sequential prompting (requires --ai_mode and --batch_mode)')
    batch_group.add_argument('--batch_mode', action='store_true', 
                            help="[AI Mode] Enable batch processing mode for automated sequential prompting")
    batch_group.add_argument('--prompts_file', type=str, 
                            help="[Batch Mode] Path to file containing prompts (required for batch mode)")
    batch_group.add_argument('--prompts_format', type=str, choices=['txt', 'json', 'jsonl'], default='txt',
                            help="[Batch Mode] Format of prompts file: 'txt' (one per line), 'json' (array), 'jsonl' (one JSON per line)")
    batch_group.add_argument('--batch_results_dir', type=str, 
                            help="[Batch Mode] Directory to save batch processing results")
    batch_group.add_argument('--batch_stop_on_error', action='store_true', 
                            help="[Batch Mode] Stop batch processing on first error")
    batch_group.add_argument('--batch_no_stream', action='store_true', 
                            help="[Batch Mode] Disable streaming in batch mode")
    
    # Standard conversion arguments group
    conversion_group = parser.add_argument_group('Standard Conversion Options', 
                                                 'Options for Excel to FHIR conversion')
    conversion_group.add_argument('--input_file', type=str, 
                                 help="Path to the input xlsx", 
                                 default="src/resources/FHIR_Cohort_Import_template.xlsx")
    conversion_group.add_argument('--output_folder', type=str, 
                                 help="Path to save the output files", 
                                 default="output/")
    conversion_group.add_argument('--format', type=str, choices=['bundle', 'ndjson'], default='bundle', 
                                 help="Output format: 'bundle' for transaction bundles (one per patient), 'ndjson' for newline-delimited JSON (one file per resource type)")
    
    # Configuration arguments group
    config_group = parser.add_argument_group('Configuration Options', 
                                            'Options for controlling FHIR resource generation behavior')
    config_group.add_argument('--config_file', type=str, 
                             help="Path to a JSON configuration file. If provided, this will be used instead of individual config arguments.", 
                             default=None)
    config_group.add_argument('--preview_mode', type=str, 
                             help="Configuration option to generate resources as 'preview mode' references will reference the entity name. Is primarily used to render a singular resource for preview.", 
                             default=False)
    config_group.add_argument('--medications_as_reference', type=str, 
                             help="Configuration option to create medication references. You may still provide medicationCodeableConcept, but a post process will convert the codeableconcepts to medication resources", 
                             default=False)
    config_group.add_argument('--build_empty_resources', type=str, 
                             help="Configuration option to build resources even when no data entries exist for that entity.", 
                             default=False)
    config_group.add_argument('--enable_default_resource_links', type=str, 
                             help="Configuration option to enable/disable automatic default resource linking.", 
                             default=True)
    config_group.add_argument('--no-default-links', action='store_true', 
                             help="Disable automatic default resource linking (shorthand for --enable_default_resource_links false)")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Handle Batch mode (requires AI mode)
    if args.batch_mode:
        if not args.ai_mode:
            logger.error("Batch mode requires --ai_mode to be enabled")
            exit(1)
        
        if not args.prompts_file:
            logger.error("Batch mode requires --prompts_file argument")
            exit(1)
        
        try:
            from langgraph_dev.batch import create_batch_processor, BatchProcessorConfig
            
            print("\n" + "="*60)
            print("FHIRSheets Batch Processing Mode")
            print("="*60)
            print("Initializing batch processor...\n")
            
            # Create batch configuration
            batch_config = BatchProcessorConfig(
                verbose=True,
                auto_save_results=True,
                results_dir=args.batch_results_dir,
                stop_on_error=args.batch_stop_on_error,
                stream=not args.batch_no_stream
            )
            
            # Create batch processor
            processor = create_batch_processor(
                working_dir=args.ai_mode_output_folder,
                batch_config=batch_config
            )
            
            # Load prompts from file
            print(f"Loading prompts from: {args.prompts_file}")
            processor.load_prompts_from_file(args.prompts_file, format=args.prompts_format)
            print(f"Loaded {len(processor.prompts)} prompts\n")
            
            # Process all prompts
            results = processor.process_all()
            
            # Display summary
            summary = processor.get_summary()
            print("\n" + "="*60)
            print("Batch Processing Summary")
            print("="*60)
            print(f"Total Prompts: {summary['total_prompts']}")
            print(f"Successful: {summary['successful']}")
            print(f"Failed: {summary['failed']}")
            print(f"Success Rate: {summary['success_rate']:.1f}%")
            print("="*60 + "\n")
            
            return
        except ImportError as e:
            logger.error(f"Batch mode requires additional dependencies. Please ensure langchain packages are installed.")
            logger.error(f"Error: {e}")
            exit(1)
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            logger.error("Please ensure your .env file is configured with API credentials.")
            exit(1)
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            exit(1)
        except Exception as e:
            logger.error(f"Error in batch mode: {e}")
            import traceback
            traceback.print_exc()
            exit(1)
    
    # Handle AI mode (interactive)
    if args.ai_mode:
        try:
            from langgraph_dev.agent import create_agent
            
            print("\n" + "="*60)
            print("FHIRSheets AI Mode")
            print("="*60)
            print("Initializing AI agent...\n")
            
            # Create agent with output folder as working directory
            agent = create_agent(working_dir=args.ai_mode_output_folder, verbose=True)
            
            # Start interactive chat
            agent.chat()
            
            return
        except ImportError as e:
            logger.error(f"AI mode requires additional dependencies. Please ensure langchain packages are installed.")
            logger.error(f"Error: {e}")
            exit(1)
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            logger.error("Please ensure your .env file is configured with API credentials.")
            exit(1)
        except Exception as e:
            logger.error(f"Error starting AI mode: {e}")
            exit(1)

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
    main(args.input_file, args.output_folder, args.format, config)

if __name__ == "__main__":
    cli()
