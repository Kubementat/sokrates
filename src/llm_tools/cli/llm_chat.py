import sys
import os
import click

from ..llm_api import LLMApi
from ..config import Config
from ..colors import Colors
from ..file_helper import FileHelper
from ..output_printer import OutputPrinter
from ..prompt_refiner import PromptRefiner
import re

@click.command()
@click.option("--api-endpoint", "-ae", default=None, help="The API endpoint for the LLM.")
@click.option("--api-key", "-ak", default=None, help="The API key for the LLM.")
@click.option("--model", "-m", default=None, help="The model to use for the LLM.")
@click.option("--temperature", "-t", default=0.7, type=float, help="The temperature for the LLM.")
@click.option("--max-tokens", "-mt", default=6000, type=float, help="The maximum amount of tokens to generate for one answer.")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output.")
@click.option("--context-text", "-ct", default=None, help="Additional context text for the LLM.")
@click.option("--context-files", "-cf", multiple=True, help="Paths to files containing additional context.")
@click.option("--context-directories", "-cd", multiple=True, help="Paths to directories containing additional context files.")
@click.option("--output-file", "-o", type=str, help="Path to a file to log the conversation.")
@click.option("--hide-reasoning", "-hr", is_flag=True, help="Hide <think> blocks from console output.")
def main(api_endpoint, api_key, model, temperature, verbose, context_text, context_files, context_directories, output_file, hide_reasoning, max_tokens):
    """
    Chat with a large language model.
    """
    config = Config()
    refiner = PromptRefiner(verbose=verbose)
    api_endpoint = api_endpoint or config.api_endpoint
    api_key = api_key or config.api_key
    model = model or config.default_model

    if not api_endpoint or not api_key or not model:
        OutputPrinter.print_error("API endpoint, API key, and model must be configured or provided.")
        sys.exit(1)
    
    llm_api = LLMApi(verbose=verbose, api_endpoint=api_endpoint, api_key=api_key)
    conversation_history = []
    log_file = None # Ensure log_file is always initialized

    if output_file:
        try:
            temp_log_file = open(output_file, "a") # Use a temporary variable
            log_file = temp_log_file # Assign to log_file only if open succeeds
            OutputPrinter.print_info("Conversation will be logged to", output_file)
        except IOError as e:
            OutputPrinter.print_error(f"Could not open output file {output_file}: {e}")
            sys.exit(1)

    # Load context
    context_content = []
    if context_text:
        context_content.append(context_text)
    if context_files:
        try:
            context_content.extend(FileHelper.read_multiple_files(list(context_files), verbose=verbose))
        except Exception as e:
            OutputPrinter.print_error(f"Error reading context files: {e}")
            sys.exit(1)
    if context_directories:
        try:
            context_content.extend(FileHelper.read_multiple_files_from_directories(list(context_directories), verbose=verbose))
        except Exception as e:
            OutputPrinter.print_error(f"Error reading context directories: {e}")
            sys.exit(1)

    if context_content:
        full_context = "\n\n".join(context_content)
        conversation_history.append({"role": "system", "content": full_context})
        if verbose:
            OutputPrinter.print_info("Loaded context", f"{full_context[:200]}...") # Show first 200 chars of context

    OutputPrinter.print_info("Starting chat. Press CTRL+D or type 'exit' to quit.", "")

    while True:
        try:
            user_input = input(f"{Colors.BLUE}You:{Colors.RESET} ")
            if user_input.lower() == "exit":
                break
            if not user_input:
                continue

            conversation_history.append({"role": "user", "content": user_input})

            if verbose:
                OutputPrinter.print_info("Sending request to LLM...", "")

            response_content_full = llm_api.chat_completion(
                messages=conversation_history,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            if response_content_full:
                # Always log the full response
                if log_file:
                    log_file.write(f"User: {user_input}\n")
                    log_file.write(f"LLM: {response_content_full}\n")
                    log_file.flush()

                display_content = response_content_full
                
                # Extract and colorize <think> block for display if not hidden
                think_match = re.search(r'<think>(.*?)</think>', display_content, re.DOTALL)
                if think_match:
                    think_content = think_match.group(1)
                    colored_think_content = f"{Colors.DIM}<think>{think_content}</think>{Colors.RESET}"
                    display_content = display_content.replace(think_match.group(0), colored_think_content)

                if hide_reasoning:
                    display_content = refiner.clean_response(display_content)
                    
                OutputPrinter.print_info(f"{Colors.GREEN}LLM", f"{display_content}{Colors.RESET}")
                conversation_history.append({"role": "assistant", "content": response_content_full})
            else:
                OutputPrinter.print_error("No response from LLM.")
                if log_file:
                    log_file.write(f"User: {user_input}\n")
                    log_file.write("LLM: No response\n")
                    log_file.flush()

        except EOFError:
            OutputPrinter.print_info("\nExiting chat.", "")
            break
        except KeyboardInterrupt:
            OutputPrinter.print_info("\nExiting chat.", "")
            break
        except Exception as e:
                OutputPrinter.print_error(f"An error occurred: {e}")
                if log_file:
                    log_file.write(f"Error: {e}\n")
                    log_file.flush()
    if log_file:
        log_file.close()

if __name__ == "__main__":
    main()