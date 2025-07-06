#!/usr/bin/env python3
# TODO: Code review this script and refine
# add temperature settings per stage

"""
Call examples

# with topic input file - teaching children about ai
./meta-prompt-generator.py \
  --topic-input-file tests/topics/ai_introduction_for_children.md \
  --prompt-generator-file prompts/prompt_generators/prompt-generator-v1.md \
  --refinement-prompt-file prompts/refine-prompt.md \
  --meta-llm-model qwen/qwen3-32b \
  --generator-llm-model qwen/qwen3-32b \
  --execution-llm-model qwen/qwen3-32b \
  --refinement-llm-model qwen/qwen3-32b \
  --api-endpoint http://localhost:1234/v1 \
  --api-key lmstudio \
  --output-directory tmp/00_teach_ai_to_children \
  --verbose

# with topic input file - ai game business plans
./meta-prompt-generator.py \
  --meta-prompt-generator-file prompts/prompt_generators/meta-prompt-generator.md \
  --topic-input-file tests/topics/ai_game_business_topic.md \
  --prompt-generator-file prompts/prompt_generators/prompt-generator-v1.md \
  --refinement-prompt-file prompts/refine-prompt.md \
  --meta-llm-model qwen/qwen3-32b \
  --generator-llm-model qwen/qwen3-32b \
  --execution-llm-model qwen/qwen3-32b \
  --refinement-llm-model qwen/qwen3-32b \
  --api-endpoint http://localhost:1234/v1 \
  --api-key lmstudio \
  --output-directory tmp/00_ai_business_plans \
  --verbose


# without topic input file
./meta-prompt-generator.py \
  --meta-prompt-generator-file prompts/prompt_generators/meta-prompt-generator.md \
  --prompt-generator-file prompts/prompt_generators/prompt-generator-v1.md \
  --refinement-prompt-file prompts/refine-prompt.md \
  --meta-llm-model josiefied-qwen3-30b-a3b-abliterated-v2 \
  --generator-llm-model josiefied-qwen3-30b-a3b-abliterated-v2 \
  --execution-llm-model josiefied-qwen3-30b-a3b-abliterated-v2 \
  --refinement-llm-model josiefied-qwen3-30b-a3b-abliterated-v2 \
  --api-endpoint http://localhost:1234/v1 \
  --api-key lmstudio \
  --output-directory tmp/00_generated_topic_qwen3_30b_a3b \
  --verbose
"""

import argparse
import sys
import os
import json
import time
import math
from pathlib import Path

from .. import Colors, Config, MetaPromptWorkflow, FileHelper

def print_header(title, color=Colors.BRIGHT_CYAN, width=60):
    """Print a beautiful header with decorative borders"""
    border = "═" * width
    print(f"\n{color}{Colors.BOLD}╔{border}╗{Colors.RESET}")
    print(f"{color}{Colors.BOLD}║{title.center(width)}║{Colors.RESET}")
    print(f"{color}{Colors.BOLD}╚{border}╝{Colors.RESET}\n")

def print_info(label, value, label_color=Colors.BRIGHT_GREEN, value_color=Colors.WHITE):
    """Print formatted info with colored labels"""
    print(f"{label_color}{Colors.BOLD}{label}:{Colors.RESET} {value_color}{value}{Colors.RESET}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.BRIGHT_RED}{Colors.BOLD}✗ {message}{Colors.RESET}")

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Meta prompt generator workflow: Meta-Prompt -> Prompt Generator -> Execution Prompts (with optional refinement)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  meta-prompt-generator.py \\
    --meta-prompt-generator-file prompts/prompt_generators/meta-prompt-generator.md \\
    --prompt-generator-file prompts/prompt_generators/prompt-generator-v1.md \\
    --refinement-prompt-file prompts/refine-concept.md \\
    --meta-llm-model unsloth-phi-4 \\
    --generator-llm-model google/gemma-3-27b \\
    --execution-llm-model qwen2.5-coder-7b-instruct-mlx \\
    --refinement-llm-model unsloth-phi-4 \\
    --api-endpoint http://localhost:1234/v1 \\
    --api-key lmstudio \\
    --output-directory tmp/multi_stage_outputs \\
    --verbose
        """
    )
    
    parser.add_argument(
        '--meta-prompt-generator-file',
        required=False,
        help='Path to the "Meta Prompt Generator Prompt" file'
    )
    
    parser.add_argument(
        '--prompt-generator-file',
        required=True,
        help='Path to the "Prompt Generator Prompt" file (defines JSON output format)'
    )
    
    parser.add_argument(
        '--refinement-prompt-file',
        required=True,
        help='Path to the refinement prompt file (for workflow extension)'
    )
    
    parser.add_argument(
        '--meta-llm-model',
        required=False,
        help='Name of the model to use for the Meta Prompt Generator step'
    )
    
    parser.add_argument(
        '--generator-llm-model',
        required=True,
        help='Name of the model to use for the Prompt Generator step'
    )
    
    parser.add_argument(
        '--execution-llm-model',
        required=True,
        help='Name of the model to use for executing the final prompts'
    )

    parser.add_argument(
        '--refinement-llm-model',
        required=True,
        help='Name of the model to use for the prompt refinement step'
    )
    
    parser.add_argument(
        '--api-endpoint',
        default="http://localhost:1234/v1",
        help='OpenAI-compatible API endpoint URL'
    )
    
    parser.add_argument(
        '--api-key',
        default="lmstudio",
        help='API key for authentication'
    )
    
    parser.add_argument(
        '--max-tokens',
        type=int,
        default=20000,
        help='Maximum tokens in response for all LLM calls (Default: 20000)'
    )
    
    parser.add_argument(
        '--temperature',
        type=float,
        default=0.7,
        help='Temperature for response generation for all LLM calls (Default: 0.7)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--output-directory',
        required=True,
        help='Directory to save the final execution prompt outputs'
    )

    parser.add_argument(
        '--topic-input-file',
        required=False,
        help='Optional: Path to a file containing the topic for prompt generation. If provided, skips meta-prompt generation.'
    )

    return parser.parse_args()

def main():
    """Main execution function"""
    print_header("🚀 Meta Prompt Generator 🚀", Colors.BRIGHT_CYAN, 60)

    args = parse_arguments()

    config = Config()
    api_endpoint = config.api_endpoint
    api_key = config.api_key
    if args.api_key:
        api_key = args.api_key
    if args.api_endpoint:
        api_endpoint = args.api_endpoint
        
    if not args.meta_prompt_generator_file and not args.topic_input_file:
        print_error(f"You must specify either a --meta-prompt-generator-file or a --topic-input-file.")
        sys.exit(1)
        
    print_info("meta-prompt-generator-file", args.meta_prompt_generator_file)
    print_info("topic-input-file", args.topic_input_file)
    print_info("prompt-generator-file", args.prompt_generator_file)
    print_info("refinement-prompt-file", args.refinement_prompt_file)
    
    print_info("meta-llm-model", args.meta_llm_model)
    print_info("generator-llm-model", args.generator_llm_model)
    print_info("execution-llm-model", args.execution_llm_model)
    print_info("refinement-llm-model", args.refinement_llm_model)
    print_info("temperature", args.temperature)
    print_info("max-tokens", args.max_tokens)
    print_info("verbose", args.verbose)
    output_directory = FileHelper.generate_postfixed_sub_directory_name(args.output_directory)
    print_info("output-directory", output_directory)

    workflow = MetaPromptWorkflow(
        api_endpoint=api_endpoint,
        api_key=api_key,
        verbose=args.verbose,
        topic_input_file=args.topic_input_file,
        meta_prompt_generator_file=args.meta_prompt_generator_file,
        refinement_prompt_file=args.refinement_prompt_file,
        prompt_generator_file=args.prompt_generator_file,
        output_directory=args.output_directory,
        generator_llm_model=args.generator_llm_model,
        refinement_llm_model=args.refinement_llm_model,
        meta_llm_model=args.meta_llm_model,
        max_tokens=args.max_tokens,
        temperature=args.temperature
    )
    workflow.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Process interrupted by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print_error(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)