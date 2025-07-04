# LLM Tools

## Introduction
This repository contains a collection of command-line tools designed to streamline working with Large Language Models (LLMs). It provides utilities for refining prompts, benchmarking model performance, managing system resources, and integrating AI capabilities into workflows.

Key features include:
- **Prompt Refinement**: Advanced modules to optimize LLM input/output through structured refinement processes
- **System Monitoring**: Real-time tracking of resource usage during LLM operations (CPU, memory, disk)
- **CLI Interface**: Extensive command-line tools (`refine`, `benchmark`, `send_prompt` and more) for rapid experimentation
- **Extensive Testing**: Built-in test infrastructure with pytest integration to ensure reliability

The project aims to make it easier for developers to experiment with LLMs through modular components, well-documented APIs, and production-ready utilities.

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

### Available Commands
The following commands are available for use via the command line:

- `benchmark-model`: Runs a benchmark test on an LLM model.
- `benchmark-results-merger`: Merges benchmark results from multiple runs.
- `benchmark-results-to-markdown`: Converts benchmark results to a Markdown report.
- `fetch-to-md`: Fetches content and converts it to Markdown format.
- `list-models`: Lists available LLM models.
- `meta-prompt-generator`: Generates meta prompts for various tasks.
- `refine-and-send-prompt`: Refines a prompt and sends it to an LLM.
- `refine-prompt`: Refines a text prompt for better results.
- `send-prompt`: Sends a prompt to an LLM and receives a response.
