# Test All Commands Script
#
# Main purpose of the script:
# This script automates testing of all CLI commands defined in the project's pyproject.toml file.
# It reads command definitions, executes each command with specified arguments, and reports success/failure.
#
# Parameters of the script:
# - COMMAND_ARGS: Dictionary mapping command names to their argument strings
# - EXCLUDEDED_COMMANDS: List of command names to exclude from testing
#
# Script call usage example:
# python test_all_commands.py

from subprocess import run
import sys
from pathlib import Path
import argparse
from datetime import datetime
from src.sokrates.colors import Colors

# prepare output directory
def prepare_output_directory():
    # Get current date and time
    timestamp = datetime.now()
    # Format it as "YYYY-MM-DD-HH_MM"
    date_string = timestamp.strftime("%Y-%m-%d-%H_%M")
    directory_path = f"tmp/test_all_results_{date_string}"
    Path(directory_path).mkdir(parents=True, exist_ok=True)
    return directory_path

TEST_OUTPUT_DIRECTORY = prepare_output_directory()
DEFAULT_MODEL = "qwen3-4b-instruct-2507-mlx"
DEFAULT_BASE_URL = "http://localhost:1234/v1"
DEFAULT_API_KEY = "not-required"

print("="*50)
print(f"TEST_OUTPUT_DIRECTORY: {TEST_OUTPUT_DIRECTORY}")
print("="*50)

def test_all_commands(api_endpoint, api_key, model):
    print(f"{Colors.BRIGHT_GREEN}TESTING COMMANDS{Colors.RESET}")

    COMMANDS = [
        {
            "cmd": "sokrates-breakdown-task",
            "args": f"--api-endpoint '{api_endpoint}' --api-key '{api_key}' -m '{model}' --task 'Get rich in 1 year' -o '{TEST_OUTPUT_DIRECTORY}/broken_tasks.json' --verbose"
        },
        {
            "cmd": "sokrates-benchmark-model",
            "args": f"--api-endpoint '{api_endpoint}' --api-key '{api_key}' --model '{model}' --input-directory tests/prompts_minimal --results-directory '{TEST_OUTPUT_DIRECTORY}/benchmark_results' --store-results"
        },
        {
            "cmd": "sokrates-execute-tasks",
            "args": f"--api-endpoint '{api_endpoint}' --api-key '{api_key}' -m '{model}' -tf tests/fixtures/tasks/black_holes.json -o '{TEST_OUTPUT_DIRECTORY}/black_holes_task.md' --verbose"
        },
        {
            "cmd": "sokrates-fetch-to-md",
            "args": f"--url 'https://de.wikipedia.org/wiki/Schwarzes_Loch' --output '{TEST_OUTPUT_DIRECTORY}/blackhole_wiki_fetched.md'"
        },
        {
            "cmd": "sokrates-idea-generator",
            "args": f"--api-endpoint '{api_endpoint}' --api-key '{api_key}' --topic-generation-model '{model}' --generator-llm-model '{model}' --execution-llm-model '{model}' --refinement-llm-model '{model}' --output-directory '{TEST_OUTPUT_DIRECTORY}/meta_ideas' --max-tokens 2000 --verbose"
        },
        {
            "cmd": "sokrates-merge-ideas",
            "args": f"--api-endpoint '{api_endpoint}' --api-key '{api_key}' -m '{model}' --verbose -o '{TEST_OUTPUT_DIRECTORY}/catdog.md' --source-documents 'tests/documents/cats.md,tests/documents/dogs.md' --max-tokens 1000"
        },
        {
            "cmd": "sokrates-refine-and-send-prompt",
            "args": f"--api-endpoint '{api_endpoint}' --api-key '{api_key}' --refinement-model '{model}' --output-model '{model}' -p 'Generate a detailed plan on how to get rich.' --output '{TEST_OUTPUT_DIRECTORY}/how_to_get_rich.md' --context-directories 'tests/contexts/testcase1' --context-files 'tests/contexts/context_formulation.md' --verbose"
        },
        {
            "cmd": "sokrates-refine-prompt",
            "args": f"--api-endpoint '{api_endpoint}' --api-key '{api_key}' -m '{model}' -p 'Generate a detailed plan on how to get rich.' --output '{TEST_OUTPUT_DIRECTORY}/how_to_get_rich_prompt_refined.md' --context-directories 'tests/contexts/testcase1' --verbose"
        },
        {
            "cmd": "sokrates-send-prompt",
            "args": f"--api-endpoint '{api_endpoint}' --api-key '{api_key}' -m '{model}' 'Hi, i would like to sell a company to the highest bidder. Please formulate a strategy and encorporate the rules of acquisition for making a good plan.' --output-directory '{TEST_OUTPUT_DIRECTORY}/send_prompt' --context-files 'src/sokrates/prompts/context/ferengi-rules-of-acquisition.md' --context-text '__You are a Ferengi from Star Trek__' --max-tokens 1000 --verbose"
        },
        {
            "cmd": "sokrates-task-add",
            "args": "-tf tests/fixtures/tasks/black_holes.json"
        },
        {
            "cmd": "sokrates-task-list",
            "args": ""
        },
        {
            "cmd": "sokrates-code-summarize",
            "args": f"--source-directory src/sokrates/coding --output '{TEST_OUTPUT_DIRECTORY}/code_summary.md' --verbose"
        },
        {
            "cmd": "sokrates-code-review",
            "args": f"--api-endpoint '{api_endpoint}' --api-key '{api_key}' -m '{model}' --files src/sokrates/llm_api.py --verbose -o '{TEST_OUTPUT_DIRECTORY}/code_reviews'"
        },
        {
            "cmd": "sokrates-code-generate-tests",
            "args": f"--api-endpoint '{api_endpoint}' --api-key '{api_key}' -m '{model}' --files src/sokrates/prompt_refiner.py -o '{TEST_OUTPUT_DIRECTORY}/generated_tests' --verbose --max-tokens 30000"
        }
    ]

    # Display all commands to be tested
    print(f"{Colors.BLUE}\n{'-'*60}{Colors.RESET}")
    print(f"{Colors.BLUE}\nCOMMAND LIST:{Colors.RESET}\n")
    for cmd in COMMANDS:
        print(f"{Colors.BLUE}{cmd['cmd']}{Colors.RESET}")
    print(f"{Colors.BLUE}\n{'-'*60}{Colors.RESET}")

    # Execute each command
    print(f"{Colors.BRIGHT_GREEN}\nTEST EXECUTION:{Colors.RESET}")
    errored_commands = []
    for cmd in COMMANDS:
        print(f"{Colors.YELLOW}\n{'-'*60}{Colors.RESET}")
        print(f"{Colors.YELLOW}\nExecuting: {cmd['cmd']} {cmd['args']}{Colors.RESET}")
        result = run(f"{cmd['cmd']} {cmd['args']}", shell=True, text=True)
        if result.returncode == 0:
            print(f"{Colors.BRIGHT_GREEN}\nSuccess.{Colors.RESET}")
        else:
            print(f"{Colors.BRIGHT_GREEN}Error: {result.stderr}{Colors.RESET}")
            errored_commands.append(cmd)
        print(f"{Colors.YELLOW}\n{'-'*60}{Colors.RESET}")

    if len(errored_commands) > 0:
        print(f"{Colors.RED}#####{Colors.RESET}")
        print(f"{Colors.RED}TEST FAILED: {len(errored_commands)} errors found.{Colors.RESET}")
        print(f"{Colors.RED}FAILING COMMANDS: {errored_commands}{Colors.RESET}")
        print(f"{Colors.RED}#####{Colors.RESET}")
        sys.exit(1)
    else:
        print(f"{Colors.GREEN}#####{Colors.RESET}")
        print(f"{Colors.GREEN}TESTS FINISHED SUCCESSFULLY.{Colors.RESET}")
        print(f"{Colors.GREEN}#####{Colors.RESET}")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Executes tasks defined in a JSON file sequentially.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--api-endpoint',
        required=False,
        default=DEFAULT_BASE_URL,
        help=f"LLM server API endpoint. Default is {DEFAULT_BASE_URL}"
    )

    parser.add_argument(
        '--api-key',
        default=DEFAULT_API_KEY,
        help='API key for authentication (many local servers don\'t require this)'
    )

    parser.add_argument(
        '--model', '-m',
        default=DEFAULT_MODEL,
        help=f"A model name to use for the test runs (default: {DEFAULT_MODEL})."
    )
    args = parser.parse_args()

    test_all_commands(api_endpoint=args.api_endpoint, 
            api_key=args.api_key, model=args.model)