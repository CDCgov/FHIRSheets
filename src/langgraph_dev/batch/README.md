# Batch Processing for FHIRSheets AI Agent

This module provides automated sequential prompting capabilities for the FHIRSheets AI Agent, allowing you to process multiple prompts in series without manual intervention.

## Overview

The batch processor enables you to:
- Queue multiple prompts and process them sequentially
- Load prompts from files (TXT, JSON, or JSONL format)
- Track processing results and statistics
- Configure error handling and output behavior
- Save results automatically to JSON files

## Quick Start

### Using the CLI

The easiest way to use batch processing is through the command-line interface:

```bash
# Create a prompts file (one prompt per line)
cat > prompts.txt << EOF
Create a new FHIR Excel file named 'patient_cohort.xlsx'
Add a Patient resource definition with entity name 'MainPatient'
Add patient data: John Doe, male, born 1980-05-15
EOF

# Run batch processing
fhir-sheets --ai_mode --batch_mode --prompts_file prompts.txt
```

### CLI Options

All batch processing options are clearly grouped in the help output:

```bash
fhir-sheets --help
```

**AI Mode Options:**
- `--ai_mode`: Enable AI-powered mode (required for batch processing)
- `--ai_mode_output_folder`: Path to save output files (default: `output_ai/`)

**Batch Processing Options** (requires `--ai_mode` and `--batch_mode`):
- `--batch_mode`: Enable batch processing mode
- `--prompts_file`: Path to file containing prompts (required)
- `--prompts_format`: Format of prompts file (`txt`, `json`, or `jsonl`)
- `--batch_results_dir`: Directory to save batch processing results
- `--batch_stop_on_error`: Stop processing on first error
- `--batch_no_stream`: Disable streaming in batch mode

### Example Commands

**Basic batch processing:**
```bash
fhir-sheets --ai_mode --batch_mode --prompts_file my_prompts.txt
```

**With custom results directory:**
```bash
fhir-sheets --ai_mode --batch_mode \
  --prompts_file my_prompts.txt \
  --batch_results_dir ./my_results
```

**Stop on first error:**
```bash
fhir-sheets --ai_mode --batch_mode \
  --prompts_file my_prompts.txt \
  --batch_stop_on_error
```

**Using JSON format prompts:**
```bash
fhir-sheets --ai_mode --batch_mode \
  --prompts_file prompts.json \
  --prompts_format json
```

## Prompts File Formats

### TXT Format (default)
One prompt per line:
```txt
Create a new FHIR Excel file named 'patients.xlsx'
Add a Patient resource definition
Add patient data: Jane Smith, female, born 1990-03-20
```

### JSON Format
Array of strings:
```json
[
  "Create a new FHIR Excel file named 'patients.xlsx'",
  "Add a Patient resource definition",
  "Add patient data: Jane Smith, female, born 1990-03-20"
]
```

### JSONL Format
One JSON object per line with a "prompt" key:
```jsonl
{"prompt": "Create a new FHIR Excel file named 'patients.xlsx'"}
{"prompt": "Add a Patient resource definition"}
{"prompt": "Add patient data: Jane Smith, female, born 1990-03-20"}
```

## Programmatic Usage

You can also use the batch processor programmatically in Python:

```python
from langgraph_dev.batch import create_batch_processor, BatchProcessorConfig

# Create custom configuration
batch_config = BatchProcessorConfig(
    verbose=True,
    auto_save_results=True,
    results_dir="./batch_results",
    stop_on_error=False,
    stream=True
)

# Create processor
processor = create_batch_processor(
    working_dir="./output_ai",
    batch_config=batch_config
)

# Add prompts
processor.add_prompts([
    "Create a new FHIR Excel file named 'observations.xlsx'",
    "Add an Observation resource definition for blood pressure",
    "Add observation data with systolic 120, diastolic 80"
])

# Or load from file
processor.load_prompts_from_file("prompts.txt", format="txt")

# Process all prompts
results = processor.process_all()

# Get summary
summary = processor.get_summary()
print(f"Success rate: {summary['success_rate']:.1f}%")
```

## Configuration

### BatchProcessorConfig

The `BatchProcessorConfig` class controls batch processing behavior:

```python
BatchProcessorConfig(
    verbose=True,                      # Enable verbose logging
    auto_save_results=True,            # Automatically save results to JSON
    results_dir=None,                  # Custom results directory (default: working_dir/batch_results)
    stop_on_error=False,               # Stop on first error
    stream=True,                       # Stream responses during processing
    clear_context_on_error=True,       # Clear context and retry on context window errors
    max_retries=3,                     # Maximum retries for context window errors
    context_window_error_keywords=None # Keywords to detect context window errors (uses defaults if None)
)
```

### Context Window Error Handling

When processing many prompts in batch mode, the conversation context can accumulate and eventually exceed the model's context window limit. The batch processor now includes automatic detection and recovery from these errors:

**How it works:**
1. The processor detects context window errors by checking for specific keywords in error messages
2. When detected, it automatically clears the conversation context by creating a new thread
3. The failed prompt is retried with the fresh context
4. This process repeats up to `max_retries` times

**Configuration:**
```python
batch_config = BatchProcessorConfig(
    clear_context_on_error=True,  # Enable automatic context clearing (default: True)
    max_retries=3,                # Retry up to 3 times (default: 3)
)
```

**Default error detection keywords:**
- "context window"
- "context_window"
- "ContextWindowExceededError"
- "Input is too long"
- "maximum context length"
- "token limit"

**Custom error keywords:**
```python
batch_config = BatchProcessorConfig(
    context_window_error_keywords=[
        "custom error pattern",
        "another pattern"
    ]
)
```

**Disabling context clearing:**
```python
batch_config = BatchProcessorConfig(
    clear_context_on_error=False  # Disable automatic retry
)
```

## Output

### Results Files

When `auto_save_results=True`, results are automatically saved to JSON files:

```
batch_results/
└── batch_results_20260820_140530.json
```

### Results Format

```json
{
  "thread_id": "batch_20260820_140530",
  "timestamp": "2026-08-20T14:05:30.123456",
  "total_prompts": 3,
  "results": [
    {
      "prompt_index": 0,
      "prompt": "Create a new FHIR Excel file named 'patients.xlsx'",
      "response": "I've created the file...",
      "success": true,
      "timestamp": "2026-08-20T14:05:31.123456",
      "retry_count": 0
    },
    {
      "prompt_index": 1,
      "prompt": "Add patient data...",
      "success": false,
      "error": "Context window exceeded...",
      "timestamp": "2026-08-20T14:05:32.123456",
      "retry_count": 3,
      "is_context_window_error": true
    },
    ...
  ]
}
```

**Result fields:**
- `prompt_index`: Index of the prompt in the batch
- `prompt`: The original prompt text
- `response`: The agent's response (if successful)
- `success`: Whether the prompt was processed successfully
- `error`: Error message (if failed)
- `timestamp`: When the result was recorded
- `retry_count`: Number of retries attempted (0 if successful on first try)
- `is_context_window_error`: Whether the error was a context window error (only present on errors)

## Callbacks

You can provide callbacks to monitor processing:

```python
def on_start(idx, prompt):
    print(f"Starting prompt {idx + 1}: {prompt[:40]}...")

def on_complete(idx, result):
    print(f"Completed prompt {idx + 1}")

def on_error(idx, error):
    print(f"Error on prompt {idx + 1}: {error}")

results = processor.process_all(
    on_prompt_start=on_start,
    on_prompt_complete=on_complete,
    on_error=on_error
)
```

## Best Practices

1. **Start Simple**: Begin with a small set of prompts to test your workflow
2. **Use Descriptive Prompts**: Clear, specific prompts lead to better results
3. **Monitor Progress**: Use verbose mode to track processing
4. **Handle Errors**: Consider using `stop_on_error=False` for long batches
5. **Save Results**: Keep `auto_save_results=True` to preserve processing history
6. **Organize Prompts**: Use meaningful file names and organize by task
7. **Context Management**: For large batches (100+ prompts), the automatic context clearing feature helps prevent context window errors
8. **Idempotent Prompts**: Design prompts to be idempotent (safe to retry) since context window errors will trigger automatic retries

## Troubleshooting

### "Batch mode requires --ai_mode to be enabled"
Make sure to include both `--ai_mode` and `--batch_mode` flags.

### "Batch mode requires --prompts_file argument"
You must specify a prompts file with `--prompts_file`.

### "Configuration error"
Ensure your `.env` file is configured with valid API credentials in `src/langgraph_dev/.env`.

### Import Errors
Batch mode requires the langchain dependencies. Ensure they are installed:
```bash
poetry install
```

### Context Window Errors
If you encounter context window exceeded errors:

1. **Automatic Recovery (Default)**: The batch processor automatically detects and recovers from context window errors by clearing the context and retrying. This is enabled by default.

2. **Check Retry Count**: Look at the `retry_count` field in the results to see how many times a prompt was retried.

3. **Adjust Max Retries**: If prompts are still failing after retries, you can increase `max_retries`:
   ```python
   batch_config = BatchProcessorConfig(max_retries=5)
   ```

4. **Manual Context Clearing**: If you want to manually control when context is cleared, you can disable automatic clearing and implement your own logic using callbacks.

5. **Reduce Prompt Complexity**: If a specific prompt consistently fails even with retries, consider breaking it into smaller, simpler prompts.

## Examples

See the CLI help for more examples:
```bash
fhir-sheets --help
```

## Architecture

The batch processing module is organized as follows:

```
src/langgraph_dev/batch/
├── __init__.py          # Module exports
├── config.py            # BatchProcessorConfig class
├── processor.py         # BatchProcessor class
└── README.md           # This file
```

The batch processor wraps the FHIRSheets AI Agent and manages:
- Prompt queuing and loading
- Sequential execution
- Result tracking and persistence
- Error handling
- Progress reporting