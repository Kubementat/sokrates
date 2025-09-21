#!/usr/bin/env python3

"""
This script sends a prompt to one or more local Large Language Model (LLM) servers,
retrieves the responses, and optionally saves them as markdown files in a specified directory.

The script supports:
1. Local or remote LLM servers via API endpoints
2. Multiple models (specified as comma-separated values)
3. Configuration of response parameters like max tokens and temperature
4. Input from file or command line
5. Output to markdown files for easy viewing/editing
"""

import argparse
import sys
import os
from pathlib import Path
from sokrates import LLMApi, FileHelper, PromptRefiner, Config
from sokrates.cli.helper import Helper
from sokrates.cli.output_printer import OutputPrinter

def write_output_file(content, model, source_prompt_file, output_directory):
    """
    Writes the content to a markdown file with appropriate naming.

    Args:
        content (str): The content to write to the output file.
        model (str): Name of the LLM model that generated the content.
        source_prompt_file (str, optional): Path to the original prompt file. 
            Used for naming if provided.
        output_directory (str, optional): Directory where the markdown file should be written.
            If None, no file is written.

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
        
        FileHelper.write_to_file(file_path=output_file, content=content)

def prompt_model(llm_api, prompt, model, max_tokens, temperature, 
    output_directory, source_prompt_file=None, post_process_results=False,
    context_text=None, context_directories=None, context_files=None, system_prompt=None):
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
        post_process_results (bool): Enable response post-processing (e.g. strip out  blocks).
        context_text (str, optional): Additional text to prepend to the prompt.
        context_directories (list, optional): List of directories containing files with context.
        context_files (list, optional): List of file paths containing additional context.
        system_prompt (str, optional): The system prompt to use for processing

    Returns:
        None
    """
    try:
        OutputPrinter.print_section(f"Querying {model} ...")
            
        context = Helper.construct_context_from_arguments(
            context_text=context_text,
            context_directories=context_directories,
            context_files=context_files)
        
        response = llm_api.send(prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            context=context,
            system_prompt=system_prompt
        )
        OutputPrinter.print_section(f"Output for model {model}")
        OutputPrinter.print(response)
        
        if post_process_results:
            refiner = PromptRefiner()
            OutputPrinter.print_section("Post processing is enabled")
            response = refiner.clean_response(response)
            OutputPrinter.print_section(f"Post processed response for model {model}")
            OutputPrinter.print(response)

        # Write response to markdown file if output directory is set
        write_output_file(response, model, source_prompt_file, output_directory)
    except Exception as e:
        OutputPrinter.print_error(f"An error occurred: {e}")
        raise(e)

def main():
    """Main function to send a prompt to one or more LLM servers and handle responses."""
    
    parser = argparse.ArgumentParser(
        description="Send prompts to LLM servers and saves responses as markdown files optionally",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        """
    )

    try:
    
        # Positional arguments (prompt)
        parser.add_argument('prompt', nargs='?', help='Text prompt to send to LLMs (optional)')
        
        parser.add_argument('--provider', default=None, help="The provider to use for the requests.")
        parser.add_argument('--api-endpoint', '-ae', default=None, help='LLM server API endpoint')
        parser.add_argument('--api-key', '-ak', default=None, help='API key for authentication (can be empty for local servers)')
        parser.add_argument('--models', '-m', default=None, help='Comma separated model names to use (can be multiple)')
        parser.add_argument('--temperature', '-t', default=None, type=float, help='Temperature for response generation')

        parser.add_argument('--system-prompt', '-sp', default=None, help='An optional system prompt to use for prompt processing by the LLM')
        parser.add_argument('--max-tokens', '-mt', default=20000, type=int, help='Maximum tokens in response (Default: 20000)')
        
        parser.add_argument('--output-directory', '-o', default=None, help='Directory to write model outputs to as markdown files')
        parser.add_argument('--input-file','-i', default=None, help='File containing the prompt to send')
        parser.add_argument('--input-directory','-d', default=None, help='Directory containing text files which should be sent as a series of separate prompts')
        parser.add_argument('--post-process-results', '-pp', action='store_true', help="Enable response post-processing (e.g. strip out  blocks)")
        parser.add_argument('--context-text', '-ct', default=None, help="Optional additional context text to prepend before the prompt")
        parser.add_argument('--context-files', '-ctf', default=None, help="Optional comma separated additional context text file paths with content that should be prepended before the prompt")
        parser.add_argument('--context-directories', '-ctd', default=None, help="Optional comma separated additional directory paths with files with content that should be prepended before the prompt")
        
        # Parse arguments
        args = parser.parse_args()
        config = Helper.load_config()
        api_endpoint = Helper.get_provider_value('api_endpoint', config, args)
        api_key = Helper.get_provider_value('api_key', config, args)
        temperature = Helper.get_provider_value('temperature', config, args, 'default_temperature')
        models = Helper.get_provider_value('models', config, args, 'default_model')
        
        # Convert models string to list if needed
        if isinstance(models, str):
            models = models.replace(" ","").split(',')
        
        # Validate input requirements
        if (args.prompt is None and args.input_file is None and args.input_directory is None):
            OutputPrinter.print_error("Either a text prompt or an --input-file or an --input-directory needs to be provided. Exiting.")
            sys.exit(1)
        
        if (args.input_file and args.input_directory):
            OutputPrinter.print_error("Both --input-file and --input-directory are provided. Choose one or the other. Exiting.")
            sys.exit(1)
        
        Helper.print_configuration_section(config=config, args=args)
        # Initialize LLM API client
        llm_api = LLMApi(api_endpoint=api_endpoint, api_key=api_key)
        
        # Handle input directory
        prompt_files = []
        if args.input_directory:
            prompt_files = FileHelper.list_files_in_directory(args.input_directory)
            OutputPrinter.print_info("Input Directory", args.input_directory)
            OutputPrinter.print_section("Input Directory contents")
            for f in prompt_files:
                OutputPrinter.print(f"  {f}")
        
        # Handle input file
        if args.input_file:
            prompt_files = [args.input_file]
        
        # Show context information
        OutputPrinter.print_info("context-text", args.context_text)
        OutputPrinter.print_info("context-directories", args.context_directories)
        OutputPrinter.print_info("context-files", args.context_files)
        
        # Process single prompt (no directory or file specified)
        if args.prompt is not None:
            for model in models:
                prompt_model(llm_api, prompt=args.prompt, model=model, max_tokens=args.max_tokens, 
                    temperature=temperature, output_directory=args.output_directory, source_prompt_file=None, 
                    post_process_results=args.post_process_results,
                    context_text=args.context_text, context_directories=args.context_directories, 
                    context_files=args.context_files, system_prompt=args.system_prompt)
            sys.exit(0)

        # Process multiple prompt files from directory
        for model in models:
            for filepath in prompt_files:  
                try:
                    prompt = FileHelper.read_file(filepath)
                except Exception as e:
                    OutputPrinter.print_error(f"Error reading input file: {e}")
                    OutputPrinter.print_info("Skipping", filepath)
                    continue

                for model in models:
                    prompt_model(llm_api, prompt=prompt, model=model, max_tokens=args.max_tokens, 
                        temperature=temperature, output_directory=args.output_directory, 
                        source_prompt_file=filepath,
                        post_process_results=args.post_process_results,
                        context_text=args.context_text, context_directories=args.context_directories, 
                        context_files=args.context_files)
    except Exception as e:
        OutputPrinter.print_error("An error occured during script execution:")
        OutputPrinter.print_error(str(e))
        sys.exit(1)

if __name__ == '__main__':
    main()
