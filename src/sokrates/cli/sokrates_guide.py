"""Interactive guide command for Sokrates — "Sokrates Teacher" persona.

This module implements the `sokrates guide` command, which starts an interactive
chat session using a teacher persona that helps users discover and learn Sokrates
CLI commands.  It reuses the existing chat infrastructure from ``sokrates_chat``
(LLM interaction, conversation logging, voice features) with a custom system
prompt that positions the LLM as an expert Sokrates guide.

Usage:
    sokrates guide [options]

Example:
    sokrates guide --provider local
"""

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

from sokrates.cli.colors import Colors
from sokrates.cli.helper import Helper
from sokrates.cli.output_printer import OutputPrinter
from sokrates.config import Config
from sokrates.file_helper import FileHelper
from sokrates.llm_api import LLMApi
from sokrates.prompt_refiner import PromptRefiner


# ---------------------------------------------------------------------------
# System prompt content
# ---------------------------------------------------------------------------

def generate_guide_system_prompt() -> str:
    """Generate the system prompt for the Sokrates Teacher guide persona.

    The prompt includes:
    1. Role definition — "Sokrates Teacher, an interactive guide for the Sokrates CLI toolkit"
    2. Capabilities summary — brief description of what Sokrates can do
    3. Full command reference — all categories and commands
    4. Behavioral instructions — practical examples, goal matching, concise responses

    Returns:
        A fully-formed system prompt string ready to be sent as a ``system`` role
        message to the LLM.
    """
    return """\
You are the Sokrates Teacher, an interactive guide for the Sokrates CLI toolkit.

## Your Role
You are an expert teacher and guide for Sokrates — a command-line toolkit for
effective Large Language Model (LLM) interactions.  Your goal is to help users
discover the right commands for their needs, understand how to use Sokrates
effectively, and get practical value from the toolkit as quickly as possible.

## What is Sokrates?
Sokrates is a comprehensive CLI toolkit that provides:
- **Prompt refinement** — optimise and clean prompts before sending to LLMs
- **AI-powered code analysis** — review, analyse, summarise, and generate tests for Python codebases
- **Background task queue** — queue long-running LLM jobs with SQLite persistence and retry logic
- **Interactive chat** — real-time chat with any OpenAI-compatible LLM endpoint
- **Workflow automation** — multi-stage idea generation, task breakdown, and content creation

Sokrates works with any OpenAI-compatible endpoint: LocalAI, Ollama, LM Studio, or custom deployments.

## Command Reference

**Prompts**
- `sokrates send-prompt` — Send a prompt to an LLM endpoint and display the response
- `sokrates refine-prompt` — Refine and optimise a prompt using an LLM before sending
- `sokrates refine-and-send-prompt` — Refine a prompt then send it in one step

**Workflows**
- `sokrates idea-generator` — Generate ideas and content using multi-stage LLM workflows
- `sokrates merge-ideas` — Merge and synthesise multiple idea documents into one
- `sokrates generate-mantra` — Generate a motivational mantra or affirmation using an LLM
- `sokrates breakdown-task` — Break down a complex task into actionable sub-tasks
- `sokrates execute-tasks` — Execute a list of tasks sequentially using an LLM

**Code Analysis**
- `sokrates code-review` — Perform an AI-powered code review on a Python codebase
- `sokrates code-analyze` — Analyse a Python codebase for complexity and quality metrics
- `sokrates code-summarize` — Generate a natural-language summary of a Python codebase
- `sokrates code-generate-tests` — Generate unit tests for Python source files automatically

**Task Queue**
- `sokrates task-add` — Add a task to the background processing queue
- `sokrates task-list` — List all tasks in the background processing queue
- `sokrates task-status` — Show the status of a specific task in the queue
- `sokrates task-remove` — Remove a task from the background processing queue
- `sokrates daemon` — Start, stop, or check the background task processing daemon

**Interactive**
- `sokrates chat` — Start an interactive chat session with an LLM
- `sokrates guide` — Start this interactive guide mode (Sokrates Teacher)

**Utilities**
- `sokrates list-models` — List available models from the configured LLM endpoint
- `sokrates fetch-to-md` — Fetch a URL and convert its content to Markdown

## How You Should Behave
- Always provide **practical, concrete examples** when explaining commands (e.g., show the exact flags to use)
- **Match the user's goal to the relevant command(s)** — ask clarifying questions if needed
- Keep responses **concise and actionable** — avoid lengthy preambles
- When a user describes a task, suggest the most relevant Sokrates command(s) and show a usage example
- Encourage users to run `sokrates <command> --help` for full option details
- If the user is new, start with a brief overview and offer to dive deeper into any area
"""


# ---------------------------------------------------------------------------
# Fallback help menu (displayed when LLM endpoint is unavailable)
# ---------------------------------------------------------------------------

def generate_fallback_help_menu() -> str:
    """Generate a static text-based help menu for when the LLM endpoint is unavailable.

    This function produces a human-readable plain-text menu that describes
    Sokrates and its commands.  It is displayed instead of the interactive
    teacher when no LLM connection can be established.

    Returns:
        A multi-line string containing the fallback help menu.
    """
    return """\
╔══════════════════════════════════════════════════════════════════╗
║              Sokrates — Offline Help Menu                       ║
╚══════════════════════════════════════════════════════════════════╝

What is Sokrates?
  Sokrates is a CLI toolkit for effective Large Language Model (LLM)
  interactions — prompt refinement, code analysis, background task
  queues, and interactive chat, all from your terminal.

Available Commands by Category
───────────────────────────────

  Prompts
    sokrates send-prompt             Send a prompt to an LLM
    sokrates refine-prompt           Refine a prompt using an LLM
    sokrates refine-and-send-prompt  Refine then send in one step

  Workflows
    sokrates idea-generator          Generate ideas via multi-stage workflows
    sokrates merge-ideas             Merge multiple idea documents
    sokrates generate-mantra         Generate a motivational mantra
    sokrates breakdown-task          Break a task into sub-tasks
    sokrates execute-tasks           Execute tasks sequentially

  Code Analysis
    sokrates code-review             AI-powered code review
    sokrates code-analyze            Complexity and quality metrics
    sokrates code-summarize          Natural-language codebase summary
    sokrates code-generate-tests     Auto-generate unit tests

  Task Queue
    sokrates task-add                Add a task to the queue
    sokrates task-list               List all queued tasks
    sokrates task-status             Check a specific task status
    sokrates task-remove             Remove a task from the queue
    sokrates daemon                  Manage the background daemon

  Interactive
    sokrates chat                    Interactive text/voice chat
    sokrates guide                   This interactive guide (requires LLM)

  Utilities
    sokrates list-models             List available LLM models
    sokrates fetch-to-md             Fetch a URL as Markdown

───────────────────────────────
Suggestions:
  • Run 'sokrates --help' for the full command listing with descriptions
  • Check your LLM endpoint configuration in ~/.sokrates/config.yml
  • Run 'sokrates guide' again once your LLM endpoint is available
"""


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Main function for the sokrates guide command.

    Starts an interactive chat session using the Sokrates Teacher system prompt.
    Reuses the LLM interaction infrastructure from sokrates_chat.py.

    If the LLM endpoint is unavailable, displays the static fallback help menu.
    Handles Ctrl+C and EOFError gracefully with a friendly goodbye message.
    """
    parser = argparse.ArgumentParser(
        description='Sokrates Guide — Interactive Sokrates Teacher powered by an LLM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            'Examples:\n\n'
            '  sokrates guide --provider local\n'
            '  sokrates guide --model qwen3-4b-instruct --provider local\n'
        ),
    )

    parser.add_argument(
        '--provider',
        required=False,
        type=str,
        default=None,
        help='The provider to use (as configured in ~/.sokrates/config.yml)',
    )
    parser.add_argument(
        '--api-endpoint', '-ae',
        default=None,
        type=str,
        help='The API endpoint for the LLM.',
    )
    parser.add_argument(
        '--api-key', '-ak',
        default=None,
        type=str,
        help='The API key for the LLM.',
    )
    parser.add_argument(
        '--model', '-m',
        default=None,
        type=str,
        help='The model to use for the LLM.',
    )
    parser.add_argument(
        '--temperature', '-t',
        default=None,
        type=float,
        help='The temperature for the LLM (0.0–1.0).',
    )
    parser.add_argument(
        '--max-tokens', '-mt',
        default=6000,
        type=float,
        help='The maximum number of tokens to generate per response.',
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output.',
    )
    parser.add_argument(
        '--output-file', '-o',
        type=str,
        help='Path to a file to log the conversation.',
    )
    parser.add_argument(
        '--hide-reasoning', '-hr',
        action='store_true',
        help='Hide <tool_call> blocks from console output.',
    )

    args = parser.parse_args()
    config = Helper.load_config()
    api_endpoint = Helper.get_provider_value('api_endpoint', config, args)
    api_key = Helper.get_provider_value('api_key', config, args)
    temperature = Helper.get_provider_value('temperature', config, args, 'default_temperature')
    model = Helper.get_provider_value('model', config, args, 'default_model')

    Helper.print_configuration_section(config=config, args=args)

    if not api_endpoint or not api_key or not model:
        OutputPrinter.print_error('API endpoint, API key, and model must be configured or provided.')
        OutputPrinter.print_info('Showing offline help menu instead:', '')
        print(generate_fallback_help_menu())
        sys.exit(1)

    OutputPrinter.print_info('Starting Sokrates Guide (Teacher Mode) with model:', model, Colors.BRIGHT_MAGENTA)

    refiner = PromptRefiner()

    # Attempt to create LLM client — if it fails, show fallback menu
    try:
        llm_api = LLMApi(api_endpoint=api_endpoint, api_key=api_key)
    except Exception as e:
        OutputPrinter.print_error(f'Could not connect to LLM endpoint: {e}')
        print(generate_fallback_help_menu())
        sys.exit(1)

    # Build initial conversation history with the teacher system prompt
    conversation_history: list[dict] = [
        {'role': 'system', 'content': generate_guide_system_prompt()},
    ]

    log_files: list = []

    # Set up default conversation log file
    home_dir = Path.home()
    default_chat_dir = home_dir / '.sokrates' / 'chats'
    default_chat_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H-%M-%S')
    default_log_file_path = default_chat_dir / FileHelper.clean_name(f'{timestamp}_guide_{model}.md')

    try:
        default_log_file = open(default_log_file_path, 'a', encoding='utf-8')
        log_files.append(default_log_file)
        OutputPrinter.print_info('Conversation will be logged to:', str(default_log_file_path))
    except IOError as e:
        OutputPrinter.print_error(f'Could not open default log file {default_log_file_path}: {e}')
        sys.exit(1)

    if args.output_file:
        try:
            extra_log_file = open(args.output_file, 'a', encoding='utf-8')
            log_files.append(extra_log_file)
            OutputPrinter.print_info('Conversation will also be logged to:', args.output_file)
        except IOError as e:
            OutputPrinter.print_error(f'Could not open output file {args.output_file}: {e}')
            sys.exit(1)

    async def chat_loop() -> None:
        """Run the interactive guide chat loop."""
        nonlocal conversation_history

        OutputPrinter.print_info(
            'Sokrates Teacher is ready.',
            "Ask me anything about Sokrates! Type 'exit' or press Ctrl+D to quit.",
        )

        while True:
            try:
                print()
                print('-' * 60)
                print()
                user_input = input(f'{Colors.BLUE}You:{Colors.RESET} ')

                if user_input.lower() in ('exit', 'quit', 'bye'):
                    print()
                    OutputPrinter.print_info(
                        "Goodbye!",
                        "Run 'sokrates guide' again to restart.",
                    )
                    break

                if not user_input.strip():
                    continue

                conversation_history.append({'role': 'user', 'content': user_input})

                OutputPrinter.print('Thinking...')

                if args.verbose:
                    OutputPrinter.print('verbose mode — Streaming response ...')
                    print('-' * 60)
                    print()

                response_content = llm_api.chat_completion(
                    messages=conversation_history,
                    model=model,
                    temperature=temperature,
                    max_tokens=args.max_tokens,
                    print_to_console=args.verbose,
                )

                if args.verbose:
                    print()
                    print('-' * 60)
                    print()

                if response_content:
                    for lf in log_files:
                        lf.write(f'User: {user_input}\n---\n')
                        lf.write(f'Sokrates Teacher: {response_content}\n---\n')
                        lf.flush()

                    display_content = response_content
                    if args.hide_reasoning:
                        display_content = refiner.clean_response(display_content)

                    print()
                    OutputPrinter.print_info(
                        f'{Colors.GREEN}Sokrates Teacher',
                        f'\n{display_content}{Colors.RESET}',
                    )
                    conversation_history.append({'role': 'assistant', 'content': response_content})
                else:
                    OutputPrinter.print_error('No response from LLM.')
                    for lf in log_files:
                        lf.write(f'User: {user_input}\n---\n')
                        lf.write('Sokrates Teacher: No response\n---\n')
                        lf.flush()

            except EOFError:
                print()
                OutputPrinter.print_info("Goodbye!", "Run 'sokrates guide' again to restart.")
                break
            except KeyboardInterrupt:
                print()
                OutputPrinter.print_info("Goodbye!", "Run 'sokrates guide' again to restart.")
                break
            except (ConnectionError, OSError, TimeoutError) as e:
                # LLM endpoint became unavailable during the session
                OutputPrinter.print_error(f'LLM endpoint unavailable: {e}')
                print()
                print(generate_fallback_help_menu())
                for lf in log_files:
                    lf.write(f'Error: LLM endpoint unavailable: {e}\n')
                    lf.flush()
                break
            except Exception as e:
                OutputPrinter.print_error(f'An error occurred: {e}')
                for lf in log_files:
                    lf.write(f'Error: {e}\n')
                    lf.flush()

        for lf in log_files:
            lf.close()

    try:
        asyncio.run(chat_loop())
    except KeyboardInterrupt:
        print()
        OutputPrinter.print_info("Goodbye!", "Run 'sokrates guide' again to restart.")
    except EOFError:
        print()
        OutputPrinter.print_info("Goodbye!", "Run 'sokrates guide' again to restart.")


if __name__ == '__main__':
    main()
