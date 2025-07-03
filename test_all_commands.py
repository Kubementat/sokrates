from subprocess import run
from src.llm_tools.colors import Colors

def test_all_commands():
    print(f"{Colors.BRIGHT_GREEN}TESTING COMMANDS{Colors.RESET}")
    
    # Command arguments can be specified at the top of this file in COMMAND_ARGS dictionary
    # Format: { "command_name": "arg1,arg2,arg3", ... }
    COMMAND_ARGS = {
        "benchmark-model": "--model 'qwen3-1.7b-mlx' --input-directory tests/prompts_minimal --results-directory tmp/benchmark_results --store-results --verbose",
        "fetch-to-md": "--url 'https://de.wikipedia.org/wiki/Schwarzes_Loch' --output tmp/blackhole.md",
        "meta-prompt-generator": "--verbose --meta-llm-model qwen3-1.7b-mlx --generator-llm-model qwen3-1.7b-mlx --execution-llm-model qwen3-1.7b-mlx --refinement-llm-model qwen3-1.7b-mlx --meta-prompt-generator-file src/llm_tools/cli/prompts/prompt_generators/meta-prompt-generator.md --prompt-generator-file src/llm_tools/cli/prompts/prompt_generators/prompt-generator-v1.md --output-directory tmp/meta_ideas --refinement-prompt-file src/llm_tools/cli/prompts/refine-prompt.md",
        "refine-and-send-prompt": "--verbose --refinement-model 'qwen3-1.7b-mlx' --output-model 'qwen3-1.7b-mlx' -p 'Generate a detailed plan on how to get rich.' --output tmp/00how_to_get_rich.md --verbose",
        "refine-prompt": "-m 'qwen3-1.7b-mlx' -p 'Generate a detailed plan on how to get rich.' --output tmp/00how_to_get_rich_refined_prompt --verbose",
        "send-prompt": "-m 'qwen3-1.7b-mlx' 'Hi, who are you?' --output-directory tmp/ --verbose"
    }
    
    EXCLUDEDED_COMMANDS = ["benchmark-results-merger", "benchmark-results-to-markdown"]

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
                cmd = f'uv run {command_name}'
                # Get arguments from COMMAND_ARGS if available
                args = COMMAND_ARGS.get(command_name, "")
                if args:
                    cmd += f" {args}"
                    
                if cmd not in EXCLUDEDED_COMMANDS:
                    COMMANDS.append({
                        "name": command_name,
                        "cmd": cmd,
                        "args": args
                    })
                else:
                    print(f"{Colors.BLUE}Commands excluded:{cmd}{Colors.RESET}")

    # Display all commands to be tested
    print(f"{Colors.BLUE}\n{'-'*60}{Colors.RESET}")
    print(f"{Colors.BLUE}\nCOMMAND LIST:{Colors.RESET}\n")
    for cmd in COMMANDS:
        print(f"{Colors.BLUE}{cmd['name'] + ':'} {cmd['cmd']}{Colors.RESET}")
    print(f"{Colors.BLUE}\n{'-'*60}{Colors.RESET}")

    # Execute each command
    print(f"{Colors.BRIGHT_GREEN}\nTEST EXECUTION:{Colors.RESET}")
    for cmd_info in COMMANDS:
        print(f"{Colors.YELLOW}\n{'-'*60}{Colors.RESET}")
        print(f"{Colors.YELLOW}\nExecuting: {cmd_info['cmd']}{Colors.RESET}")
        result = run(cmd_info['cmd'], shell=True, text=True)
        if result.returncode == 0:
            print(f"{Colors.BRIGHT_GREEN}\nSuccess.{Colors.RESET}")
        else:
            print(f"{Colors.BRIGHT_GREEN}Error: {result.stderr}{Colors.RESET}")
        print(f"{Colors.YELLOW}\n{'-'*60}{Colors.RESET}")

test_all_commands()