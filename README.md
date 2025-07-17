# LLM Tools Library

## Introduction
This repository contains a collection of command-line tools, classes and functions designed to streamline working with Large Language Models (LLMs). It provides utilities for refining prompts, benchmarking model performance, managing system resources, and integrating AI capabilities into workflows.

Key features include:
- **Prompt Refinement**: Advanced modules to optimize LLM input/output through structured refinement processes
- **System Monitoring**: Real-time tracking of resource usage during LLM operations (CPU, memory, disk)
- **CLI Interface**: Extensive command-line tools (`refine`, `benchmark`, `send_prompt` and more) for rapid experimentation
- **Extensive Testing**: Built-in test infrastructure with pytest integration to ensure reliability

The project aims to make it easier for developers to experiment with LLMs through modular components, well-documented APIs, and production-ready utilities.

## Table of Contents

1. [Introduction](#introduction)
2. [Modules](#modules)
3. [Setup Instructions](#setup-instructions)
4. [Script List](#script-list)
5. [CLI Tools](#cli-tools)
6. [Running the Project](#running-the-project)

## Contributing

We welcome contributions from the community! Please follow these guidelines:

1. Fork the repository and create a new branch for your feature or bug fix.
2. Add appropriate tests to cover your changes.
3. Ensure all tests pass before submitting a pull request.
4. Update documentation as needed.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Colors Module (colors.py)
- colors.add_color(): Adds color to text strings
- colors.remove_color(): Removes color from text strings
- colors.get_color_schemes(): Gets all available color schemes

## File Helpers Module (file_helper.py)
- file_helper.get_file_names_in_dir(): Lists all files in a directory
- file_helper.get_lines_from_file(): Gets lines from a file
- file_helper.write_to_file(): Writes content to a file
- file_helper.append_to_file(): Appends content to a file

## LLM API Module (llm_api.py)
- llm_api.generate_text(): Generates text using an LLM
- llm_api.summarize_text(): Summarizes text using an LLM
- llm_api.answer_question(): Answers questions using an LLM

## System Monitor Module (system_monitor.py)
- system_monitor.get_process_info(): Gets information about running processes
- system_monitor.get_disk_usage(): Gets disk usage statistics
- system_monitor.get_memory_usage(): Gets memory usage statistics

## Prompt Refiner Module (prompt_refiner.py)
These functions help optimize and compare AI prompts.
- `prompt_refiner.refine_prompt()`: Refines a text prompt for better results
- `prompt_refiner.compare_prompts()`: Compares two different prompts

### Setup Instructions:
```bash
$ git clone https://github.com/Kubementat/llm_tools.git
$ cd llm_tools
$ uv sync
$ uv run pytest -v
```

### Running the Project

#### Run the testsuite
To test all CLI commands with example arguments, you can use the `test_all_commands.py` script:
```bash
$ python test_all_commands.py
```

This will execute each command defined in the project's pyproject.toml file with specified arguments and report success/failure.

#### Production Mode
For production usage, you can run individual commands as needed. For example:

```bash
# List available models
$ uv run list-models --api-endpoint http://localhost:1234/v1

# Benchmark a model
$ uv run benchmark-model --api-endpoint http://localhost:1234/v1 --models "qwen/qwen3-8b"

# Generate a mantra
$ uv run generate-mantra --api-endpoint http://localhost:1234/v1 --output mantra.txt

# Refine and send a prompt
$ uv run refine-and-send-prompt --input "What is AI?" --refinement-instructions refinement.md --api-endpoint http://localhost:1234/v1
```

### Available Commands
The following commands are available for use via the command line:

- `benchmark-model`: Runs a benchmark test on an LLM model.
- `benchmark-results-merger`: Merges benchmark results from multiple runs.
- `benchmark-results-to-markdown`: Converts benchmark results to a Markdown report.
- `fetch-to-md`: Fetches content and converts it to Markdown format.
- `list-models`: Lists available LLM models.
- `idea-generator`: Generates and details out ideas.
- `refine-and-send-prompt`: Refines a prompt and sends it to an LLM.
- `refine-prompt`: Refines a text prompt for better results.
- `send-prompt`: Sends a prompt to an LLM and receives a response.

## CLI Tools

### `benchmark-model` - Runs benchmark tests on LLM models
uv run benchmark-model --api-endpoint http://localhost:1234/v1 --models "qwen/qwen3-8b"

### `benchmark-results-merger` - Merges benchmark results from multiple runs
uv run benchmark-results-merger --input-dir results/ --output results/merged.md

### `benchmark-results-to-markdown` - Converts benchmark results to Markdown report
uv run benchmark-results-to-markdown --input results.json --output results.md

### `fetch-to-md` - Fetches content and converts it to Markdown format
uv run fetch-to-md --url https://example.com --output output.md

### `list-models` - Lists available LLM models
uv run list-models --api-endpoint http://localhost:1234/v1

### `idea-generator` - Generates ideas
uv run idea-generator --topic-input-file topics/ai_introduction.md --output-dir outputs/

### `refine-and-send-prompt` - Refines and sends prompts to LLM
uv run refine-and-send-prompt --input "What is AI?" --refinement-instructions refinement.md --api-endpoint http://localhost:1234/v1

### `refine-prompt` - Refines text prompts for better results
uv run refine-prompt --input "Explain quantum computing" --refinement-instructions refinement.md --api-endpoint http://localhost:1234/v1

### `send-prompt` - Sends a prompt to an LLM and receives a response
uv run send-prompt --models "qwen/qwen3-8b" --input "What is AI?" --output outputs/response.md
