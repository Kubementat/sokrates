# LLM Tools Library Documentation

This document provides a concise overview of the `llm_tools` Python library, designed to facilitate interactions with Large Language Models (LLMs) and related workflows.

## Package Overview (`__init__.py`)
The `llm_tools` directory is a Python package. Its `__init__.py` file exposes various modules and their contents directly under the `llm_tools` namespace for easier access and import.

## `colors.py`
### `Colors` Class
Provides ANSI escape codes for console text formatting, including regular colors, bright colors, text styles (bold, dim, italic, underline, blink, reverse, strikethrough), and background colors. Used to enhance terminal output.

## `config.py`
### `Config` Class
Manages application-wide configuration settings. It loads environment variables from a `.env` file, providing default values for API endpoints, API keys, and the default LLM model.
- `__init__(verbose=False)`: Initializes the Config object, loading environment variables.
- `load_env()`: Loads environment variables from the specified `.env` file.

## `file_helper.py`
### `FileHelper` Class
Provides static methods for common file system operations.
- `clean_name(name: str) -> str`: Cleans a string for use as a filename or path component.
- `list_files_in_directory(directory_path: str, verbose: bool = False) -> List[str]`: Lists all files directly within a specified directory.
- `read_file(file_path: str, verbose: bool = False) -> str`: Reads and returns the entire content of a specified file.
- `read_multiple_files(file_paths: List[str], verbose: bool = False) -> List[str]`: Reads and returns the content of multiple files.
- `read_multiple_files_from_directories(directory_paths: List[str], verbose: bool = False) -> List[str]`: Reads and returns the content of all files within multiple specified directories.
- `write_to_file(file_path: str, content: str, verbose: bool = False) -> None`: Writes content to a file, creating parent directories if needed.
- `create_new_file(file_path: str, verbose: bool = False) -> None`: Creates a new empty file, creating parent directories if needed.
- `generate_postfixed_sub_directory_name(base_directory: str) -> str`: Generates a new subdirectory name with a datetime postfix.
- `combine_files(file_paths: List[str], verbose: bool = False) -> str`: Combines content of multiple files into a single string, separated by '---'.
- `combine_files_in_directories(directory_paths: List[str], verbose: bool = False) -> str`: Combines content of all files from multiple directories into a single string, separated by '---'.

## `llm_api.py`
### `LLMApi` Class
Handles interactions with OpenAI-compatible LLM APIs.
- `__init__(verbose: bool = False, api_endpoint: str = Config.DEFAULT_API_ENDPOINT, api_key: str = Config.DEFAULT_API_KEY)`: Initializes the client.
- `get_openai_client() -> OpenAI`: Returns an OpenAI client instance.
- `list_models() -> List[str]`: Lists available models from the endpoint.
- `send(prompt: str, model: str = Config.DEFAULT_MODEL, context: str = None, context_array: List[str] = None, max_tokens: int = 2000, temperature: float = 0.7) -> str`: Sends a text prompt for generation.
- `chat_completion(messages: List[dict], model: str = Config.DEFAULT_MODEL, max_tokens: int = 2000, temperature: float = 0.7) -> str`: Sends messages for chat completion.
- `combine_context(context: List[str]) -> str`: Combines a list of context strings into a single string.

## `lmstudio_benchmark.py`
### `LMStudioBenchmark` Class
Benchmarks LLMs, especially those compatible with LM Studio's OpenAI-like API.
- `__init__(api_endpoint: str = "http://localhost:1234/v1")`: Initializes the benchmark with the API endpoint.
- `monitor_system() -> None`: Monitors system resources (CPU, memory, GPU) in a separate thread.
- `benchmark_model(model_name: str, prompts: list[str], max_tokens: int = 100, temperature: float = 0.7, results_directory: str = None, timeout: int = 240) -> dict`: Benchmarks a single LLM model.
- `_save_response_to_file(results_directory: str, model_name: str, prompt_index: int, response_data: dict, temperature: float) -> None`: Saves full LLM response content to a Markdown file.
- `analyze_results(results: dict, store_results: bool = False, results_directory: str = None) -> None`: Analyzes and displays benchmark results.
- `save_results(results: dict, results_directory: str = None) -> None`: Saves comprehensive benchmark results to a JSON file.
- `create_comparison_table(all_model_results: list[dict]) -> tuple[str, dict]`: Creates a human-readable comparison table and structured data for multiple models.
- `save_comparison_results(comparison_data: dict, results_directory: str = None, filename_prefix: str = "") -> None`: Saves structured model comparison results to a JSON file.
- `benchmark_multiple_models(model_names: list[str], prompts: list[str], max_tokens: int = 100, temperature: float = 0.7, store_results: bool = False, results_directory: str = None, timeout: int = 240) -> list[dict]`: Orchestrates benchmarking for multiple models.

## `meta_prompt_workflow.py`
### `MetaPromptWorkflow` Class
Orchestrates a multi-step workflow for generating, refining, and executing LLM prompts.
- `__init__(api_endpoint: str, api_key: str, ...)`: Initializes the workflow with various file paths and LLM models for different stages.
- `generate_or_set_topic() -> str`: Generates an initial topic using a meta-prompt or reads it from a file.
- `execute_prompt_generation() -> list[str]`: Generates a list of execution prompts based on a template and the initial topic.
- `refine_and_execute_prompt(execution_prompt: str, index: int) -> str`: Refines and executes a given prompt.
- `run() -> None`: Executes the full meta-prompt workflow, including topic generation, prompt generation, refinement, execution, and output saving.

## `output_printer.py`
### `OutputPrinter` Class
Provides static methods for printing formatted and colored output to the console.
- `print_header(title: str, color: str = Colors.BRIGHT_CYAN, width: int = 60) -> None`: Prints a decorative header.
- `print_section(title: str, color: str = Colors.BRIGHT_BLUE, char: str = "─") -> None`: Prints a section separator.
- `print_info(label: str, value: str, label_color: str = Colors.BRIGHT_GREEN, value_color: str = Colors.WHITE) -> None`: Prints formatted information.
- `print_success(message: str) -> None`: Prints a success message.
- `print_warning(message: str) -> None`: Prints a warning message.
- `print_error(message: str) -> None`: Prints an error message.
- `print_progress(message: str) -> None`: Prints a progress message.
- `print_file_created(filename: str) -> None`: Prints a message for file creation.

## `prompt_refiner.py`
### `PromptRefiner` Class
Provides utility functions for processing and cleaning text generated by LLMs.
- `__init__(config: dict = {}, verbose: bool = False)`: Initializes the refiner.
- `combine_refinement_prompt(input_prompt: str, refinement_prompt: str) -> str`: Combines an initial prompt with a refinement prompt.
- `format_as_markdown(content: str) -> str`: Ensures content is formatted as Markdown.
- `clean_response(response: str) -> str`: Cleans LLM-generated responses by removing meta-elements and extraneous prefixes.
- `clean_response_from_markdown(content: str) -> str`: Removes Markdown code block formatting from content.

## `refinement_workflow.py`
### `RefinementWorkflow` Class
Orchestrates prompt refinement and execution processes.
- `__init__(api_endpoint: str = Config.DEFAULT_API_ENDPOINT, api_key: str = Config.DEFAULT_API_KEY, model: str = Config.DEFAULT_MODEL, max_tokens: int = 20000, temperature: float = 0.7, verbose: bool = False) -> None`: Initializes the workflow.
- `refine_prompt(input_prompt: str, refinement_prompt: str) -> str`: Refines an input prompt using an LLM.
- `refine_and_send_prompt(input_prompt: str, refinement_prompt: str, refinement_model: str = None, execution_model: str = None, refinement_temperature: float = None) -> str`: Refines and then sends the prompt to an LLM for execution.
- `generate_mantra(context_files: List[str] = None, task_file_path: str = None) -> str`: Generates a "mantra" based on provided context and a task file.

## `system_monitor.py`
### `SystemMonitor` Class
Monitors system resources (CPU, memory, GPU) in real-time.
- `__init__(interval: float = 0.5)`: Initializes the monitor.
- `_monitor_system_loop()`: Internal loop to continuously monitor system resources in a separate thread.
- `start()`: Starts the system monitoring in a separate thread.
- `stop()`: Stops the monitoring thread and returns collected statistics.
- `get_system_info() -> dict`: Gathers static system information.

## `voice_helper.py`
### `WhisperModel` Enum
Enum for available Whisper models (BASE, TINY, MEDIUM, LARGE).

### `AudioRecorder` Class
Handles audio recording and saving to a WAV file.
- `__init__(model: str = WhisperModel.BASE.value)`: Initializes the recorder.
- `record_audio()`: Records audio from the microphone.
- `save_recording(filename: str)`: Saves recorded audio frames to a WAV file.

### Functions
- `play_audio_file(filename: str)`: Plays an audio file.
- `run_voice_chat(llm_api, model: str, temperature: float, max_tokens: int, conversation_history: list, log_files: list, hide_reasoning: bool, verbose: bool, refiner)`: Runs a voice-based chat interaction with an LLM.