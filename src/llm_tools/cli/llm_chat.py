"""
LLM Chat CLI - Command-line interface for interacting with large language models.

Main Purpose:
Provides a CLI for interacting with LLMs supporting model selection, 
temperature adjustment, context management, and conversation logging.

Parameters:
  --api-endpoint (-ae): LLM API endpoint (required if not in config)
  --api-key (-ak): API key for authentication (required if not in config)
  --model (-m): LLM model identifier (default: qwen/qwen3-8b)
  --temperature (-t): Sampling temperature (0.0-1.0, default: 0.7)
  --max-tokens (-mt): Maximum response tokens (default: 6000)
  --verbose (-v): Enable verbose output
  --context-text (-ct): Additional context for LLM processing
  --context-files (-cf): Paths to files containing context
  --context-directories (-cd): Paths to directories with context files
  --output-file (-o): Path to log conversation history
  --hide-reasoning (-hr): Hide reasoning in responses

Usage Example:
  python llm_chat.py \\
    --model qwen/qwen3-8b \\
    --temperature 0.8 \\
    --max-tokens 1024 \\
    --context-files ./context/prompt.md \\
    --output-file chat_log.txt
"""

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
from datetime import datetime
from pathlib import Path
from ..voice_helper import run_voice_chat # Import the voice chat function
import asyncio # Import asyncio for running async functions

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
@click.option("--voice", "-V", is_flag=True, help="Enable voice chat mode.") # Add voice flag
def main(api_endpoint, api_key, model, temperature, verbose, context_text, context_files, context_directories, output_file, hide_reasoning, max_tokens, voice):
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
    log_files = [] # Initialize as a list to hold all log file handles

    # Setup default log file
    home_dir = Path.home()
    default_chat_dir = home_dir / ".llm-tools" / "chats"
    default_chat_dir.mkdir(parents=True, exist_ok=True) # Create directory if it doesn't exist

    timestamp = datetime.now().strftime("%Y%m%d_%H-%M-%S")
    default_log_file_path = default_chat_dir / FileHelper.clean_name(f"{timestamp}_{model}.md")

    try:
        default_log_file = open(default_log_file_path, "a")
        log_files.append(default_log_file)
        OutputPrinter.print_info("Conversation will be logged to default file:", str(default_log_file_path))
    except IOError as e:
        OutputPrinter.print_error(f"Could not open default log file {default_log_file_path}: {e}")
        sys.exit(1)

    # If --output-file is specified, open it as well
    if output_file:
        try:
            extra_log_file = open(output_file, "a")
            log_files.append(extra_log_file)
            OutputPrinter.print_info("Conversation will also be logged to:", output_file)
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

    # Define a function for the chat loop to allow switching between modes
    async def chat_loop(voice_mode):
        nonlocal conversation_history # Allow modification of conversation_history from outer scope
        
        while True:
            try:
                if voice_mode:
                    OutputPrinter.print_info("Starting voice chat. Press CTRL+C to exit.", "")
                    action = await run_voice_chat(llm_api, model, temperature, max_tokens, conversation_history, log_files, hide_reasoning, verbose, refiner)
                    if action == "toggle_voice":
                        voice_mode = not voice_mode
                        OutputPrinter.print_info(f"Switched to {'voice' if voice_mode else 'text'} mode.", "")
                        continue
                    elif isinstance(action, tuple) and action[0] == "add_context":
                        filepath = action[1]
                        try:
                            context_content = FileHelper.read_file(filepath)
                            conversation_history.append({"role": "system", "content": context_content})
                            OutputPrinter.print_info(f"Added context from {filepath}", "")
                        except Exception as e:
                            OutputPrinter.print_error(f"Error reading context file {filepath}: {e}")
                        continue
                    elif action == "exit":
                        break
                else:
                    OutputPrinter.print_info("Starting text chat. Press CTRL+D or type 'exit' to quit.", "")
                    OutputPrinter.print_info("Commands: /add <Filepath> or /voice", "")
                    user_input = input(f"{Colors.BLUE}You:{Colors.RESET} ")
                    if user_input.lower() == "exit":
                        break
                    elif user_input.lower() == "/voice":
                        voice_mode = not voice_mode
                        OutputPrinter.print_info(f"Switched to {'voice' if voice_mode else 'text'} mode.", "")
                        continue
                    elif user_input.lower().startswith("/add "):
                        filepath = user_input[5:].strip()
                        try:
                            context_content = FileHelper.read_file(filepath)
                            conversation_history.append({"role": "system", "content": context_content})
                            OutputPrinter.print_info(f"Added context from {filepath}", "")
                        except Exception as e:
                            OutputPrinter.print_error(f"Error reading context file {filepath}: {e}")
                        continue
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
                        # Always log the full response to all open log files
                        for lf in log_files:
                            lf.write(f"User: {user_input}\n---\n")
                            lf.write(f"LLM: {response_content_full}\n---\n")
                            lf.flush()

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
                        for lf in log_files:
                            lf.write(f"User: {user_input}\n---\n")
                            lf.write("LLM: No response\n---\n")
                            lf.flush()

            except EOFError:
                OutputPrinter.print_info("\nExiting chat.", "")
                break
            except KeyboardInterrupt:
                OutputPrinter.print_info("\nExiting chat.", "")
                break
            except Exception as e:
                    OutputPrinter.print_error(f"An error occurred: {e}")
                    for lf in log_files:
                        lf.write(f"Error: {e}\n")
                        lf.flush()
        
        # Close all open log files
        for lf in log_files:
            lf.close()

    asyncio.run(chat_loop(voice))

if __name__ == "__main__":
    main()