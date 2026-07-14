# FHIRSheets

FhirSheets is a command-line tool that reads an Excel file in FHIR cohort format and generates FHIR bundle JSON files from it. Each row in the template Excel file is used to create an individual JSON file, outputting them to a specified folder.

## Table of Contents
- [FHIRSheets](#fhirsheets)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage](#Usage)

## Features
- Reads an Excel file following the FHIR cohort import template.
- Converts each row in the Excel file to a FHIR bundle JSON file.
- Exports generated JSON files to a specified output folder.

## Requirements
- Python 3.x
- Required Python packages (see `requirements.txt`)

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/CDCgov/synthetic-data.git
   cd fhir-python-cohort-generation
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
   Or use poetry
   ```bash
   poetry build
   ```
## Usage
1. **Fill Out the Template:**
   - Open the template file `src/resources/Fhir_Cohort_Import_Template.xlsx`.
   - Fill out each row with the relevant data.

2. **Run the Tool:**
   - Use the `python -m src.cli.fhirsheets` module script with the required arguments:
     - `--input-file`: The path to the input Excel file.
     - `--output-folder`: The path to the output folder where the JSON files will be saved.

   ```bash
   python -m src.fhir_sheets.cli.main --input_file src/resources/Fhir_Cohort_Import_Template.xlsx --output_folder /path/to/output/folder
3. The tool will generate one FHIR bundle JSON file for each row defined in the template.

## Example

```bash
python -m src.fhir_sheets.cli.main --input_file src/resources/Fhir_Cohort_Import_Template.xlsx --output_folder ./output_bundles
```
In this example, each row in the `Fhir_Cohort_Import_Template.xlsx` file will be processed, and a corresponding JSON file will be generated in the `output_bundles` folder.

## Configuration

FHIRSheets supports configuration through JSON files or command-line arguments to customize behavior, including default resource references.

### Using a Configuration File

Create a JSON configuration file (e.g., `my_config.json`):

```json
{
  "enable_default_resource_links": true,
  "default_resource_references": [
    ["observation", "patient", "subject"],
    ["procedure", "patient", "subject"]
  ]
}
```

Then use it with the CLI:

```bash
python -m src.fhir_sheets.cli.main --input_file input.xlsx --output_folder output/ --config_file my_config.json
```

### Configuration Options

- **`enable_default_resource_links`** (boolean, default: `true`): Enable/disable automatic default resource linking
- **`default_resource_references`** (array): Customize which default resource references to create automatically
- **`array_type_references`** (array): Specify which references should be arrays
- **`preview_mode`** (boolean, default: `false`): Generate resources in preview mode
- **`medications_as_reference`** (boolean, default: `false`): Convert medicationCodeableConcept to medication resources
- **`build_empty_resources`** (boolean, default: `false`): Build resources even when no data exists

### Command-Line Arguments

You can also pass configuration options directly:

```bash
python -m src.fhir_sheets.cli.main \
  --input_file input.xlsx \
  --output_folder output/ \
  --enable_default_resource_links true \
  --build_empty_resources false
```

Or use the convenient flag to disable default resource links:

```bash
python -m src.fhir_sheets.cli.main \
  --input_file input.xlsx \
  --output_folder output/ \
  --no-default-links
```

**Note:** For advanced configuration like customizing `default_resource_references` lists, use a JSON config file.

### Example Configuration File

See `config_example.json` for a complete example with all default values and available options.

### Programmatic Usage

When using FHIRSheets as a Python library, use the simplified context-based API:

```python
from fhir_sheets.core.config.FhirSheetsConfiguration import FhirSheetsConfiguration
from fhir_sheets.core.conversion import create_transaction_bundle, ConversionContext
from fhir_sheets.core import read_input
import json

# Load configuration from JSON file
with open('my_config.json', 'r') as f:
    config_dict = json.load(f)
config = FhirSheetsConfiguration(config_dict)

# Read input data
resource_defs, resource_links, cohort_data = read_input.read_xlsx_and_process("input.xlsx")

# Create context object (encapsulates all parameters)
ctx = ConversionContext(
    resource_definitions=resource_defs,
    resource_links=resource_links,
    cohort_data=cohort_data,
    index=0,
    config=config
)

# Generate bundle with simplified signature
bundle = create_transaction_bundle(ctx)
```

#### Processing Multiple Patients

The context-based approach makes it easy to process multiple patients:

```python
from fhir_sheets.core.conversion import create_transaction_bundle, ConversionContext

# Read input data once
resource_defs, resource_links, cohort_data = read_input.read_xlsx_and_process("input.xlsx")

# Process all patients
bundles = []
for patient_index in range(len(cohort_data.patients)):
    ctx = ConversionContext(
        resource_definitions=resource_defs,
        resource_links=resource_links,
        cohort_data=cohort_data,
        index=patient_index,
        config=config
    )
    bundle = create_transaction_bundle(ctx)
    bundles.append(bundle)
```

## License
This project is licensed under the MIT License. See the `LICENSE` file for more information.
