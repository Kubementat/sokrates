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
    """
    Main function that tests all CLI commands defined in pyproject.toml.

    Functionality:
    - Reads command definitions from pyproject.toml under [project.scripts] section
    - Executes each command with specified arguments (from COMMAND_ARGS)
    - Reports success/failure for each command execution
    - Exits with error code 1 if any command fails, otherwise exits with 0

    Arguments:
    None (uses global variables COMMAND_ARGS and EXCLUDEDED_COMMANDS)

    Return value:
    None (exits program with appropriate exit code)
    """
    print(f"{Colors.BRIGHT_GREEN}TESTING COMMANDS{Colors.RESET}")

    # Command arguments can be specified at the top of this file in COMMAND_ARGS dictionary
    # Format: { "command_name": "arg1,arg2,arg3", ... }
    COMMAND_ARGS = {
        "breakdown-task": "--task 'Get rich in 1 year'",
        "benchmark-model": "--model 'qwen3-1.7b-mlx' --input-directory tests/prompts_minimal --results-directory tmp/benchmark_results --store-results",
        "execute-tasks": "-m 'qwen/qwen3-4b' -tf tests/tasks/cat_minzi.json -o tmp/minzi_task_execution_results_01",
        "fetch-to-md": "--url 'https://de.wikipedia.org/wiki/Schwarzes_Loch' --output tmp/blackhole.md",
        "idea-generator": "--output-directory tmp/meta_ideas",
        "refine-and-send-prompt": "--refinement-model 'qwen3-1.7b-mlx' --output-model 'qwen3-1.7b-mlx' -p 'Generate a detailed plan on how to get rich.' --output tmp/00how_to_get_rich.md --context-directories 'tests/contexts/testcase1' --context-files 'tests/contexts/context_formulation.md'",
        "refine-prompt": "-m 'qwen3-1.7b-mlx' -p 'Generate a detailed plan on how to get rich.' --output tmp/00how_to_get_rich_refined_prompt --context-directories 'tests/contexts/testcase1'",
        "send-prompt": "-m 'qwen3-1.7b-mlx' 'Hi, write a short article about who you are and what you can do' --output-directory tmp/ --context-directories 'tests/contexts/testcase1' --context-files 'tests/contexts/context_formulation.md' --context-text '__You are a Ferengi from Star Trek__'"
    }

    EXCLUDEDED_COMMANDS = ["llmchat", "benchmark-results-merger", "benchmark-results-to-markdown"]

    # Get command names from pyproject.toml
    COMMANDS = []
    with open('pyproject.toml', 'r') as f:
        lines = f.readlines()
        start_section = False
        for line in lines:
            if line.strip() == '[project.scripts]':
                start_section = True
                continue
            if start_section and '=' in line:
                command_name = line.split('=')[0].strip()

                if command_name in EXCLUDEDED_COMMANDS:
                    continue

                cmd = f'uv run {command_name}'
                # Get arguments from COMMAND_ARGS if available
                args = COMMAND_ARGS.get(command_name, "")
                if args:
                    cmd += f" {args}"

                COMMANDS.append({
                    "name": command_name,
                    "cmd": cmd,
                    "args": args
                })

    # Excluded commands
    print(f"{Colors.BRIGHT_BLUE}\n{'-'*60}{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLUE}\nEXCLUDED_COMMANDS:{Colors.RESET}\n")
    for cmd in EXCLUDEDED_COMMANDS:
        print(f"{Colors.BRIGHT_BLUE}{cmd}{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLUE}\n{'-'*60}{Colors.RESET}")

    # Display all commands to be tested
    print(f"{Colors.BLUE}\n{'-'*60}{Colors.RESET}")
    print(f"{Colors.BLUE}\nCOMMAND LIST:{Colors.RESET}\n")
    for cmd in COMMANDS:
        print(f"{Colors.BLUE}{cmd['name'] + ':'} {cmd['cmd']}{Colors.RESET}")
    print(f"{Colors.BLUE}\n{'-'*60}{Colors.RESET}")

    # Execute each command
    print(f"{Colors.BRIGHT_GREEN}\nTEST EXECUTION:{Colors.RESET}")
    errors_found = 0
    for cmd_info in COMMANDS:
        print(f"{Colors.YELLOW}\n{'-'*60}{Colors.RESET}")
        print(f"{Colors.YELLOW}\nExecuting: {cmd_info['cmd']}{Colors.RESET}")
        result = run(cmd_info['cmd'], shell=True, text=True)
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