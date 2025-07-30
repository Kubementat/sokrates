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
from src.sokrates.colors import Colors

def test_all_commands():
    print(f"{Colors.BRIGHT_GREEN}TESTING COMMANDS{Colors.RESET}")

    COMMANDS = [
        {
            "cmd": "sokrates-breakdown-task",
            "args": "-m 'qwen/qwen3-4b' --task 'Get rich in 1 year'"
        },
        {
            "cmd": "sokrates-benchmark-model",
            "args": "--model 'qwen3-1.7b-mlx' --input-directory tests/prompts_minimal --results-directory tmp/benchmark_results --store-results"
        },
        {
            "cmd": "sokrates-execute-tasks",
            "args": "-m 'qwen/qwen3-4b' -tf tests/tasks/black_holes.json -o tmp/black_hole_task_execution_results_01"
        },
        {
            "cmd": "sokrates-fetch-to-md",
            "args": "--url 'https://de.wikipedia.org/wiki/Schwarzes_Loch' --output tmp/blackhole.md"
        },
        {
            "cmd": "sokrates-idea-generator",
            "args": "--topic-generation-model 'qwen/qwen3-4b' --generator-llm-model 'qwen/qwen3-4b' --execution-llm-model 'qwen/qwen3-4b' --refinement-llm-model 'qwen/qwen3-4b' --output-directory tmp/meta_ideas"
        },
        {
            "cmd": "sokrates-refine-and-send-prompt",
            "args": "--refinement-model 'qwen3-1.7b-mlx' --output-model 'qwen3-1.7b-mlx' -p 'Generate a detailed plan on how to get rich.' --output tmp/00how_to_get_rich.md --context-directories 'tests/contexts/testcase1' --context-files 'tests/contexts/context_formulation.md'"
        },
        {
            "cmd": "sokrates-refine-prompt",
            "args": "-m 'qwen3-1.7b-mlx' -p 'Generate a detailed plan on how to get rich.' --output tmp/00how_to_get_rich_refined_prompt --context-directories 'tests/contexts/testcase1'"
        },
        {
            "cmd": "sokrates-send-prompt",
            "args": "-m 'qwen3-1.7b-mlx' 'Hi, i would like to sell a company to the highest bidder. Please formulate a strategy and encorporate the rules of acquisition for making a good plan.' --output-directory tmp/ --context-files 'src/sokrates/prompts/context/ferengi-rules-of-acquisition.md' --context-text '__You are a Ferengi from Star Trek__'"
        },
        {
            "cmd": "sokrates-task-add",
            "args": "-tf tests/tasks/black_holes.json"
        },
        {
            "cmd": "sokrates-task-list",
            "args": ""
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
    errors_found = 0
    for cmd in COMMANDS:
        print(f"{Colors.YELLOW}\n{'-'*60}{Colors.RESET}")
        print(f"{Colors.YELLOW}\nExecuting: {cmd['cmd']} {cmd['args']}{Colors.RESET}")
        result = run(f"{cmd['cmd']} {cmd['args']}", shell=True, text=True)
        if result.returncode == 0:
            print(f"{Colors.BRIGHT_GREEN}\nSuccess.{Colors.RESET}")
        else:
            print(f"{Colors.BRIGHT_GREEN}Error: {result.stderr}{Colors.RESET}")
            errors_found+=1
        print(f"{Colors.YELLOW}\n{'-'*60}{Colors.RESET}")

    if errors_found > 0:
        print(f"{Colors.RED}{"-"*60}{Colors.RESET}")
        print(f"{Colors.RED}TEST FAILED: {errors_found} errors found.{Colors.RESET}")
        print(f"{Colors.RED}{"-"*60}{Colors.RESET}")
        sys.exit(1)
    else:
        print(f"{Colors.GREEN}{"-"*60}{Colors.RESET}")
        print(f"{Colors.GREEN}TESTS FINISHED SUCCESSFULLY.{Colors.RESET}")
        print(f"{Colors.GREEN}{"-"*60}{Colors.RESET}")
        sys.exit(0)

test_all_commands()
