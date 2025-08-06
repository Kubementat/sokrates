#!/usr/bin/env python3

"""
This script sends a prompt to one or more local Large Language Model (LLM) servers,
retrieves the responses, and optionally saves them as markdown files in a specified directory.

The script supports:
1. Local or remote LLM servers via API endpoints
2. Multiple models (specified as comma-separated values)
3. Configuration of response parameters like max tokens and temperature
4. Input from file or command line
5. Verbose output and error handling
6. Output to markdown files for easy viewing/editing

Call example:
./send-prompt.py --models "qwen2.5-coder-7b-instruct-mlx,josiefied-qwen3-30b-a3b-abliterated-v2" --input-directory tmp/input_prompts --max-tokens 10000 -o tmp/outputs --verbose
"""

import click
import sys
import logging
import os
from pathlib import Path
from openai import OpenAI
from .. import LLMApi, FileHelper, PromptRefiner, Config

# ANSI escape codes for colors
COLOR_RESET = "\033[0m"
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_MAGENTA = "\033[95m"
COLOR_CYAN = "\033[96m"
COLOR_BOLD = "\033[1m"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def write_output_file(content, model, source_prompt_file, output_directory, verbose=False):
    """
    Writes the content to a markdown file with appropriate naming.

    Args:
        content (str): The content to write to the output file.
        model (str): Name of the LLM model that generated the content.
        source_prompt_file (str, optional): Path to the original prompt file. 
            Used for naming if provided.
        output_directory (str, optional): Directory where the markdown file should be written.
            If None, no file is written.
        verbose (bool): If True, prints additional information about the operation.

    Returns:
        None
    """
    if output_directory is not None:    
        clean_model_name = FileHelper.clean_name(model)
        output_file = os.path.join(output_directory, f"output_{clean_model_name}.md")
        
        # if there were multiple prompt files -> add postfix
        if source_prompt_file is not None:
            source_file_name = FileHelper.clean_name(Path(source_prompt_file).stem)
            output_file = os.path.join(output_directory, f"output_{clean_model_name}_{source_file_name}.md")
        
        FileHelper.write_to_file(file_path=output_file, content=content, verbose=verbose)

def prompt_model(llm_api, prompt, model, max_tokens, temperature, 
    output_directory, source_prompt_file=None, verbose=False, post_process_results=False,
    context_text=None, context_directories=None, context_files=None):
    """Process a prompt with a specific LLM model and handle the response.

    This function sends a prompt to an LLM server using the provided configuration,
    handles the response, and optionally saves it as a markdown file.

    Args:
        llm_api (LLMApi): The LLM API client instance to use for sending prompts.
        prompt (str): The text prompt to send to the LLM.
        model (str): Name of the LLM model to use for generation.
        max_tokens (int): Maximum number of tokens in the response.
        temperature (float): Controls randomness in response generation.
        output_directory (str, optional): Directory where markdown files should be written.
        source_prompt_file (str, optional): Path to the original prompt file for naming.
        verbose (bool): If True, prints additional information about operations.
        post_process_results (bool): Enable response post-processing (e.g. strip out  blocks).
        context_text (str, optional): Additional text to prepend to the prompt.
        context_directories (list, optional): List of directories containing files with context.
        context_files (list, optional): List of file paths containing additional context.

    Returns:
        None
    """
    try:
        logging.info(f"{COLOR_MAGENTA}{'-'*20}{COLOR_RESET}")
        logging.info(f"{COLOR_MAGENTA}{COLOR_BOLD}\nQuerying {model} ... \n{COLOR_RESET}")
            
        context_array = []
        if context_text:
            context_array.append(context_text)
        if context_directories:
            directories = [s.strip() for s in context_directories.split(",")]
            context_array.extend(FileHelper.read_multiple_files_from_directories(directories, verbose=verbose))
        if context_files:
            files = [s.strip() for s in context_files.split(",")]
            context_array.extend(FileHelper.read_multiple_files(files, verbose=verbose))

        response = llm_api.send(prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            context_array=context_array
        )
        logging.info(f"{COLOR_MAGENTA}{'-'*20}{COLOR_RESET}")
        logging.info(f"{COLOR_MAGENTA}{COLOR_BOLD}\nOutput for model {model} :\n{COLOR_RESET}")
        logging.info(f"{COLOR_MAGENTA}{'-'*20}\n{COLOR_RESET}")
        logging.info(response)
        logging.info(f"{COLOR_MAGENTA}{'-'*20}\n{COLOR_RESET}")
        
        if post_process_results:
            refiner = PromptRefiner({}, verbose=verbose)
            logging.info(f"{COLOR_MAGENTA}{COLOR_BOLD}\nPost processing is enabled\n{COLOR_RESET}")
            response = refiner.clean_response(response)
            logging.info(f"{COLOR_MAGENTA}{COLOR_BOLD}\nPost processed response for model {model} :\n{COLOR_RESET}")
            logging.info(response)
            logging.info(f"{COLOR_MAGENTA}{'-'*20}\n{COLOR_RESET}")

        # Write response to markdown file if output directory is set
        write_output_file(response, model, source_prompt_file, output_directory, verbose)
    except Exception as e:
        logging.error(f"{COLOR_RED}{COLOR_BOLD}An error occurred: {e}{COLOR_RESET}")
        raise(e)

@click.command()
@click.argument('prompt', required=False)
@click.option('--api-endpoint', '-ae', default=Config().api_endpoint, help='LLM server API endpoint')
@click.option('--api-key', '-ak', default=Config().api_key, help='API key for authentication (can be empty for local servers)')
@click.option('--models', '-m', default=Config().default_model, help='Comma separated model names to use (can be multiple)')
@click.option('--max-tokens', '-mt', default=20000, type=int, help='Maximum tokens in response (Default: 20000)')
@click.option('--temperature', '-t', default=Config().default_model_temperature, type=float, help='Temperature for response generation')
@click.option('--verbose','-v', is_flag=True, help='Enable verbose output')
@click.option('--output-directory', '-o', default=None, help='Directory to write model outputs to as markdown files')
@click.option('--input-file','-i', default=None, help='File containing the prompt to send')
@click.option('--input-directory','-d', default=None, help='Directory containing text files which should be sent as a series of separate prompts')
@click.option('--post-process-results', '-pp', is_flag=True, help="Enable response post-processing (e.g. strip out <think> blocks)")
@click.option('--context-text', '-ct', default=None, required=False, help="Optional additional context text to prepend before the prompt")
@click.option('--context-files', '-ctf', default=None, required=False, help="Optional comma separated additional context text file paths with content that should be prepended before the prompt")
@click.option('--context-directories', '-ctd', default=None, required=False, help="Optional comma separated additional directory paths with files with content that should be prepended before the prompt")
def main(prompt, api_endpoint, api_key, models, max_tokens, temperature, verbose, output_directory, input_file, input_directory, post_process_results, context_text, context_directories, context_files):
    """Main function to send a prompt to one or more LLM servers and handle responses.

    Args:
        prompt: The input text to send to the LLMs
        api_endpoint: URL of the LLM server API
        api_key: Authentication key for the API
        models: Comma-separated list of model names to query
        max_tokens: Maximum number of tokens in the response
        temperature: Controls randomness in response generation (lower = more deterministic)
        verbose: Flag to enable detailed output
        output_directory: Directory where markdown outputs should be saved (optional)
        input_file: Path to file containing prompt text (reads from command line if None)
        input_directory: Directory path with prompt text files (optional)
        post_process_results: Flag to enable response post-processing (e.g. strip out <think> blocks)
        context_text: Text to include in the prompt (optional)
        context_directories: List of directories containing prompt text files (optional)
        context_files: List of files containing prompt text (optional)
    Returns:
        None
    """
    llm_api = LLMApi(api_endpoint=api_endpoint, api_key=api_key, verbose=verbose)
    
    if prompt is None and input_file is None and input_directory is None:
        logging.error(f"{COLOR_RED}{COLOR_BOLD}Either a text prompt or an --input-file or an --input-directory needs to be provided. Exiting.{COLOR_RESET}")
        sys.exit(1)
    
    if input_file and input_directory:
        logging.error(f"{COLOR_RED}{COLOR_BOLD}Both --input-file and --input-directory are provided. Choose one or the other. Exiting.{COLOR_RESET}")
        sys.exit(1)
    
    # Convert models string to list if needed
    if isinstance(models, str):
        models = models.split(',')
    
    # read multiple file paths if provided    
    prompt_files = []
    if input_directory:
        prompt_files = FileHelper.list_files_in_directory(input_directory,verbose)
        logging.info(f"{COLOR_MAGENTA}Input Directory: {input_directory}{COLOR_RESET}")
        logging.info(f"{COLOR_MAGENTA}Prompt Files: {COLOR_RESET}")
        logging.info(f"{COLOR_MAGENTA}{prompt_files}{COLOR_RESET}")
    
    # Read prompt from file if specified
    if input_file:
        prompt_files = [input_file]
        
    if verbose:
        logging.info(f"{COLOR_MAGENTA}context-text: {context_text}{COLOR_RESET}")
        logging.info(f"{COLOR_MAGENTA}context-directories: {context_directories}{COLOR_RESET}")
        logging.info(f"{COLOR_MAGENTA}context-files: {context_files}{COLOR_RESET}")
        
    # only prompt is given , no file or directory -> execute for this file
    if prompt is not None:
        for model in models:
            prompt_model(llm_api, prompt=prompt, model=model, max_tokens=max_tokens, 
                temperature=temperature, output_directory=output_directory, source_prompt_file=None, 
                verbose=verbose, post_process_results=post_process_results,
                context_text=context_text, context_directories=context_directories, 
                context_files=context_files)
            sys.exit(0)

    for model in models:
        for filepath in prompt_files:  
            try:
                prompt = FileHelper.read_file(filepath,verbose)
            except Exception as e:
                logging.error(f"{COLOR_RED}{COLOR_BOLD}Error reading input file: {e}{COLOR_RESET}")
                logging.info(f"{COLOR_MAGENTA}Skipping {filepath}{COLOR_RESET}")
                next

            for model in models:
                prompt_model(llm_api, prompt=prompt, model=model, max_tokens=max_tokens, 
                    temperature=temperature, output_directory=output_directory, source_prompt_file=filepath, 
                    verbose=verbose, post_process_results=post_process_results,
                    context_text=context_text, context_directories=context_directories, 
                    context_files=context_files)

        
if __name__ == '__main__':
    main()
