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

### After Installation

Once installed (via `pip install fhir-sheets` or `poetry install`), you can use the `fhir-sheets` command directly:

1. **Fill Out the Template:**
   - Open the template file `src/resources/Fhir_Cohort_Import_Template.xlsx`.
   - Fill out each row with the relevant data.

2. **Run the Tool:**
   - Use the `fhir-sheets` command with the required arguments:
     - `--input_file`: The path to the input Excel file.
     - `--output_folder`: The path to the output folder where the JSON files will be saved.

   ```bash
   fhir-sheets --input_file src/resources/Fhir_Cohort_Import_Template.xlsx --output_folder /path/to/output/folder
   ```

3. The tool will generate one FHIR bundle JSON file for each row defined in the template.

### Development Usage (Without Installation)

If you're developing and haven't installed the package, you can still run it using Python's module syntax:

```bash
python -m fhir_sheets.cli.main --input_file src/resources/Fhir_Cohort_Import_Template.xlsx --output_folder /path/to/output/folder
```

## Example

```bash
fhir-sheets --input_file src/resources/Fhir_Cohort_Import_Template.xlsx --output_folder ./output_bundles
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
fhir-sheets --input_file input.xlsx --output_folder output/ --config_file my_config.json
```

### Advanced Configuration Options

- **`enable_default_resource_links`** (boolean, default: `true`): Enable/disable automatic default resource linking
- **`default_resource_references`** (array): Customize which default resource references to create automatically
- **`array_type_references`** (array): Specify which references should be arrays
- **`preview_mode`** (boolean, default: `false`): generate resources as "preview mode" references within the FHIR Resouces will reference the entity name, rather than a generated id. Is primarily used to render a singular resource for preview.
- **`medications_as_reference`** (boolean, default: `false`): Convert medicationCodeableConcept to medication resources
- **`build_empty_resources`** (boolean, default: `false`): Build entities resources even when no data exists

### Command-Line Arguments

You can also pass configuration options directly:

```bash
fhir-sheets \
  --input_file input.xlsx \
  --output_folder output/ \
  --enable_default_resource_links true \
  --build_empty_resources false
```

Or use the convenient flag to disable default resource links:

```bash
fhir-sheets \
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

## AI Mode - Interactive FHIR Resource Generation

FHIRSheets includes an AI-powered interactive mode that uses natural language to generate FHIR resources.

### Setup

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Configure environment:**
   ```bash
   cp src/langgraph_dev/.env.example src/langgraph_dev/.env
   ```

3. **Edit `.env` with your API key:**
   ```bash
   OPENAI_API_KEY=sk-your-key-here
   OPENAI_MODEL_NAME=gpt-4
   ```

### Using AI Mode

Start the interactive AI assistant:

```bash
fhir-sheets --ai-mode --output_folder ./output
```

The AI agent will guide you through creating FHIR resources using natural language:

```
You: Create a new FHIR file called patient_data.xlsx

AI: I'll create a new FHIR Excel file for you...
[Creates file and confirms]

You: Add a patient named John Doe, born on 1990-05-15

AI: I'll add that patient to the file...
[Creates Patient resource with the specified data]

You: Add a diabetes diagnosis for this patient

AI: I'll create a Condition resource for diabetes...
[Creates linked Condition resource]

You: Generate the FHIR bundles

AI: Generating FHIR bundles from the Excel file...
[Generates JSON output files]
```

Type `exit`, `quit`, or `q` to leave AI mode.

### Available Tools

#### Low-Level XLSX Tools (`FHIRSheetsXLSXTool`)

- **`create_new_file`** - Create new FHIR Excel files from template
- **`create_resource_definition`** - Add/update resource definitions (auto-copies reference columns)
- **`create_resource_link`** - Add resource links between entities
- **`set_patient_data_value`** - Set patient data values (0-based row indexing)
- **`generate_fhir_bundles`** - Generate FHIR bundles from Excel file
- And more...

#### High-Level Resource Builders (`FHIRSheetsResourceBuilderTool`)

Simplified tools for creating complete FHIR resources:

- **`create_patient`** - Patient demographics
- **`create_practitioner`** - Healthcare providers
- **`create_encounter`** - Patient encounters
- **`create_condition`** - Diagnoses/conditions
- **`create_medication_request`** - Medication orders
- **`create_vital_sign`** - Vital signs observations
- And 11 more resource types...

### Usage Example

```python
from langgraph_dev.tools.fhirsheets_xlsx_tool import FHIRSheetsXLSXTool
from langgraph_dev.tools.fhirsheets_resource_builder_tool import FHIRSheetsResourceBuilderTool

# Initialize tools
xlsx_tool = FHIRSheetsXLSXTool()
builder = FHIRSheetsResourceBuilderTool(xlsx_tool)

# Create a patient
builder.create_patient.invoke({
    "entity_name": "PrimaryPatient",
    "row_index": 0,
    "given_name": "John",
    "family_name": "Doe"
})
```

## License
This project is licensed under the MIT License. See the `LICENSE` file for more information.
