#!/usr/bin/env python3
# TODO: Code review this script and refine
# add temperature settings per stage

"""
Call examples

# with topic input file - teaching children about ai
./meta-prompt-generator.py \
  --meta-prompt-generator-file prompts/prompt_generators/meta-prompt-generator.md \
  --topic-input-file tests/topics/ai_introduction_for_children.md \
  --prompt-generator-file prompts/prompt_generators/prompt-generator-v1.md \
  --refinement-prompt-file prompts/refine-prompt.md \
  --meta-llm-model qwen/qwen3-32b \
  --generator-llm-model qwen/qwen3-32b \
  --execution-llm-model qwen/qwen3-32b \
  --refinement-llm-model qwen/qwen3-32b \
  --api-endpoint http://localhost:1234/v1 \
  --api-token lmstudio \
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
  --api-token lmstudio \
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
  --api-token lmstudio \
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

from .. import LLMApi, PromptRefiner, Colors, FileHelper

def print_header(title, color=Colors.BRIGHT_CYAN, width=60):
    """Print a beautiful header with decorative borders"""
    border = "═" * width
    print(f"\n{color}{Colors.BOLD}╔{border}╗{Colors.RESET}")
    print(f"{color}{Colors.BOLD}║{title.center(width)}║{Colors.RESET}")
    print(f"{color}{Colors.BOLD}╚{border}╝{Colors.RESET}\n")

def print_section(title, color=Colors.BRIGHT_BLUE, char="─"):
    """Print a section separator"""
    print(f"\n{color}{Colors.BOLD}{char * 50}{Colors.RESET}")
    print(f"{color}{Colors.BOLD} {title}{Colors.RESET}")
    print(f"{color}{Colors.BOLD}{char * 50}{Colors.RESET}")

def print_info(label, value, label_color=Colors.BRIGHT_GREEN, value_color=Colors.WHITE):
    """Print formatted info with colored labels"""
    print(f"{label_color}{Colors.BOLD}{label}:{Colors.RESET} {value_color}{value}{Colors.RESET}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}✓ {message}{Colors.RESET}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.BRIGHT_YELLOW}{Colors.BOLD}⚠ {message}{Colors.RESET}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.BRIGHT_RED}{Colors.BOLD}✗ {message}{Colors.RESET}")

def print_progress(message):
    """Print progress message"""
    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}⟳ {message}{Colors.RESET}")

def print_file_created(filename):
    """Print file creation message"""
    print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}📄 Created: {Colors.RESET}{Colors.CYAN}{filename}{Colors.RESET}")

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
    --api-token lmstudio \\
    --output-directory tmp/multi_stage_outputs \\
    --verbose
        """
    )
    
    parser.add_argument(
        '--meta-prompt-generator-file',
        required=True,
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
        required=True,
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
        '--api-token',
        default="lmstudio",
        help='API token for authentication'
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
    
    start_time = time.time()

    args = parse_arguments()

    llm_api = LLMApi(api_endpoint=args.api_endpoint, api_key=args.api_key, verbose=args.verbose)
    prompt_refiner = PromptRefiner(verbose=args.verbose)

    generated_prompt_generator_content = None
    if args.topic_input_file:
        print_section("1. Using Topic Input File for Prompt Generation", Colors.BRIGHT_BLUE)
        try:
            generated_prompt_generator_content = FileHelper.read_file(args.topic_input_file, args.verbose)
            print_success(f"Successfully loaded topic from {args.topic_input_file}.")
            if args.verbose:
                print_info("Topic Content (first 200 chars)", generated_prompt_generator_content[:200] + "...", Colors.BRIGHT_MAGENTA)
        except Exception as e:
            print_error(f"Error loading topic input file: {e}")
            sys.exit(1)
    else:
        # --- Step 1: Send Meta Prompt Generator Prompt to LLM ---
        print_section("1. Generating Prompt Generator Prompt", Colors.BRIGHT_BLUE)
        try:
            meta_prompt_content = FileHelper.read_file(args.meta_prompt_generator_file, args.verbose)
            print_progress(f"Sending Meta Prompt Generator to {args.meta_llm_model}...")
            
            generated_prompt_generator_content = llm_api.send(
                prompt=meta_prompt_content,
                model=args.meta_llm_model,
                max_tokens=args.max_tokens,
                temperature=args.temperature
            )
            
            # cleanup result
            generated_prompt_generator_content = prompt_refiner.clean_response(generated_prompt_generator_content)
            
            print_success("Successfully generated Prompt Generator Prompt.")
            if args.verbose:
                print_info("Generated Prompt Generator (first 200 chars)", generated_prompt_generator_content[:200] + "...", Colors.BRIGHT_MAGENTA)
                
        except Exception as e:
            print_error(f"Error in Meta Prompt Generator step: {e}")
            sys.exit(1)

    # --- Step 2: Send Prompt Generator Prompt to LLM to get Execution Prompts ---
    print_section("2. Generating Execution Prompts (JSON)", Colors.BRIGHT_BLUE)
    try:
        prompt_generator_template = FileHelper.read_file(args.prompt_generator_file, args.verbose)
        
        # Combine the generated prompt generator content with the template that defines JSON output
        combined_generator_prompt = f"{prompt_generator_template}\n{generated_prompt_generator_content}"
        
        print_progress(f"Sending combined Prompt Generator to {args.generator_llm_model}...")
        
        json_response_content = llm_api.send(
            prompt=combined_generator_prompt,
            model=args.generator_llm_model,
            max_tokens=args.max_tokens,
            temperature=args.temperature
        )
        
        # default response cleanup
        json_response_content = prompt_refiner.clean_response(json_response_content)
        # cleanup any markdown as this should be pure json for parsing
        json_response_content = prompt_refiner.clean_response_from_markdown(json_response_content)
        
        print_success("Successfully generated JSON of Execution Prompts.")

        generated_prompts_filename = os.path.join(args.output_directory, "generated_prompts.json")
        FileHelper.save_content_to_file(json_response_content, generated_prompts_filename, args.verbose)
        print_file_created(generated_prompts_filename)
        
        # Attempt to parse JSON
        try:
            parsed_json = json.loads(json_response_content)
            execution_prompts = parsed_json.get("prompts", [])
            if not execution_prompts:
                print_warning("No 'prompts' array found in the generated JSON or it was empty.")
                sys.exit(1)
            print_info("Number of Execution Prompts generated", len(execution_prompts), Colors.BRIGHT_MAGENTA)
        except json.JSONDecodeError as e:
            print_error(f"Failed to parse JSON response from Prompt Generator: {e}")
            print_error(f"Raw JSON response: {json_response_content[:500]}...")
            sys.exit(1)
            
    except Exception as e:
        print_error(f"Error in Prompt Generator step: {e}")
        sys.exit(1)

    # --- Step 3: Refine and Send Each Execution Prompt to LLM ---
    print_section("3. Refining and Executing Each Prompt", Colors.BRIGHT_BLUE)
    refinement_prompt_template = FileHelper.read_file(args.refinement_prompt_file, args.verbose)

    created_files = []
    for i, execution_prompt in enumerate(execution_prompts):
        print_section(f"Executing Prompt {i+1}/{len(execution_prompts)}", Colors.BRIGHT_GREEN, "=")
        
        try:
            # Refinement step
            print_progress(f"Refining Execution Prompt {i+1} with {args.refinement_llm_model}...")
            combined_refinement_prompt = prompt_refiner.combine_refinement_prompt(
                execution_prompt, refinement_prompt_template
            )
            
            refined_response = llm_api.send(
                prompt=combined_refinement_prompt,
                model=args.refinement_llm_model,
                max_tokens=args.max_tokens,
                temperature=args.temperature
            )
            cleaned_refined_prompt = prompt_refiner.clean_response(refined_response)
            print_success(f"Successfully refined Execution Prompt {i+1}.")
            if args.verbose:
                print_info("Refined Prompt (first 200 chars)", cleaned_refined_prompt[:200] + "...", Colors.BRIGHT_MAGENTA)

            # Execution step
            print_progress(f"Sending refined prompt {i+1} to {args.execution_llm_model} for execution...")
            final_execution_response = llm_api.send(
                prompt=cleaned_refined_prompt,
                model=args.execution_llm_model,
                max_tokens=args.max_tokens,
                temperature=args.temperature
            )
            # cleanup final result again
            final_execution_response = prompt_refiner.clean_response(final_execution_response)
            
            print_success(f"Successfully executed Prompt {i+1}.")
            
            # Save output
            output_filename = os.path.join(
                args.output_directory,
                f"output_execution_prompt_{i+1}_{FileHelper.clean_name(args.execution_llm_model)}.md"
            )
            FileHelper.save_content_to_file(final_execution_response, output_filename, args.verbose)
            created_files.append(output_filename)
            print_file_created(output_filename)

        except Exception as e:
            print_error(f"Error processing Execution Prompt {i+1}: {e}")
            print_warning(f"Skipping Execution Prompt {i+1} due to error.")
            continue # Continue to the next prompt even if one fails

    # Final summary
    # measure time
    end_time = time.time()
    total_time_elapsed_in_seconds = round(end_time - start_time, 2)
    total_time_elapsed_in_minutes = round(total_time_elapsed_in_seconds / 60.0,2)
    
    print_header("🎉 Workflow Completed! 🎉", Colors.BRIGHT_GREEN, 60)
    print_info(f"Total execution time: {round(total_time_elapsed_in_minutes, 2)} minutes  - {round(total_time_elapsed_in_seconds,2)} seconds", Colors.BRIGHT_MAGENTA)
    if created_files:
        print_section("Generated Files", Colors.BRIGHT_GREEN)
        for f in created_files:
            print_file_created(f)
    else:
        print_warning("No output files were generated.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Process interrupted by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print_error(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)