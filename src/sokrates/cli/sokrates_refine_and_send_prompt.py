#!/usr/bin/env python3
"""
LLM Prompt Refinement and Send script

This script refines prompts using one model and then
sends the refined prompt to another model for the actual task execution,
leveraging the LLMApi and PromptRefiner classes.
"""

import argparse
import sys
from pathlib import Path
from .helper import Helper
from sokrates import LLMApi, PromptRefiner, Colors, FileHelper, Config
from sokrates.cli.output_printer import OutputPrinter

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Refine prompts using one LLM and send to another for execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
"""
    )
    
    parser.add_argument(
        '--refinement-model', '-rm',
        required=False,
        default=None,
        help="Name of the model to use for prompt refinement."
    )
    
    parser.add_argument(
        '--output-model', '-om',
        required=False,
        default=None,
        help="Name of the model to receive the refined prompt and to generate the final output."
    )
    
    parser.add_argument(
        '--refinement-temperature', '-rt',
        type=float,
        default=None,
        help="Temperature for the refinement model (Default: 0.7)."
    )
    
    parser.add_argument(
        '--output-temperature', '-ot',
        type=float,
        default=None,
        help="Temperature for the output model (default: 0.2)"
    )
    
    parser.add_argument(
        '--refinement-prompt-file', '-rpf',
        required=False,
        help='Path to file containing refinement instructions. Default is: prompts/refine-prompt.md'
    )
    
    parser.add_argument(
        '--text-prompt', '-p',
        required=False,
        help='Initial text prompt to send to the LLM (not required if --input-file is used)'
    )
    
    parser.add_argument(
        '--input-file', '-i',
        required=False,
        help='Path to file containing the initial prompt to refine'
    )
    
    parser.add_argument(
        '--provider',
        required=False,
        type=str,
        default=None,
        help="The provider to use"
    )

    parser.add_argument(
        '--api-endpoint',
        default=None,
        required=False,
        help='OpenAI-compatible API endpoint URL'
    )
    
    parser.add_argument(
        '--api-key',
        default=None,
        required=False,
        help='API key for authentication'
    )
    
    parser.add_argument(
        '--max-tokens-refinement', '-mtr',
        type=int,
        default=5000,
        help='the maximum number of tokens generated during prompt refinement. Default: 5000'
    )
    
    parser.add_argument(
        '--max-tokens-output', '-mto',
        type=int,
        default=5000,
        help='the maximum number of tokens generated during the final output task. Default: 5000'
    )
    
    parser.add_argument(
        '--output', '-o',
        required=False,
        help='Path to file where the final LLM response will be saved'
    )
    
    # context
    parser.add_argument(
        '--context-text', '-ct',
        default=None,
        help='Optional additional context text to prepend before the prompt'
    )
    parser.add_argument(
        '--context-files', '-cf',
        help='Optional comma separated additional context text file paths with content that should be prepended before the prompt'
    )
    parser.add_argument(
        '--context-directories', '-cd',
        default=None,
        help='Optional comma separated additional directory paths with files with content that should be prepended before the prompt'
    )
    
    return parser.parse_args()


def main():
    """Main execution function"""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                 sokrates - Prompt Refinement Workflow        ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    # Parse arguments
    args = parse_arguments()
    
    config = Helper.load_config()
    api_endpoint = Helper.get_provider_value('api_endpoint', config, args)
    api_key = Helper.get_provider_value('api_key', config, args)
    
    output_model = Helper.get_provider_value('output_model', config, args, 'default_model')
    refinement_model = Helper.get_provider_value('refinement_model', config, args, 'default_model')
    refinement_temperature = Helper.get_provider_value('refinement_temperature', config, args, 'default_temperature')
    output_temperature = Helper.get_provider_value('output_temperature', config, args, 'default_temperature')
    
    # Validate temperature ranges
    if not (0.0 <= refinement_temperature <= 1.0):
        print(f"{Colors.RED}Refinement temperature must be between 0.0 and 1.0{Colors.RESET}")
        sys.exit(1)
    
    if not (0.0 <= output_temperature <= 1.0):
        print(f"{Colors.RED}Output model temperature must be between 0.0 and 1.0{Colors.RESET}")
        sys.exit(1)

    refinement_prompt_file = args.refinement_prompt_file
    if not args.refinement_prompt_file:
        refinement_prompt_file = (config.get('prompts_directory') / 'refine-prompt.md').resolve()
        print(f"{Colors.BLUE}No refinement prompt file provided. Using default: {refinement_prompt_file}{Colors.RESET}")
        
    if not Path(refinement_prompt_file).exists():
        print(f"{Colors.RED}Refinement prompt file not found: {refinement_prompt_file}{Colors.RESET}")
        sys.exit(1)
        
    if not args.input_file and not args.text_prompt:
        print(f"{Colors.RED}No --input-file or --text-prompt parameters provided. Exiting.{Colors.RESET}")
        sys.exit(1)

    Helper.print_configuration_section(config=config, args=args)
    OutputPrinter.print_info("Refinement Model", refinement_model)
    OutputPrinter.print_info("Refinement Temperature", refinement_temperature)
    OutputPrinter.print_info("Output Model", output_model)
    OutputPrinter.print_info("Output Temperature", output_temperature)

    # context
    context = Helper.construct_context_from_arguments(
        context_text=args.context_text,
        context_directories=args.context_directories,
        context_files=args.context_files)

    # Initialize LLMApi, PromptRefiner
    llm_api = LLMApi(api_endpoint=api_endpoint, api_key=api_key)
    prompt_refiner = PromptRefiner()

    # Step 1: Read input files
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{Colors.BLUE}🔄 Reading input files")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    try:
        # refinement prompt
        refinement_prompt_content = FileHelper.read_file(refinement_prompt_file)
        print(f"{Colors.GREEN}Successfully read file: {refinement_prompt_file}{Colors.RESET}")
        print(f"{Colors.BLUE}File size: {len(refinement_prompt_content)} characters{Colors.RESET}")
        
        # input prompt
        input_prompt_content = ""
        if args.text_prompt:
            input_prompt_content = args.text_prompt
        else:
            input_prompt_content = FileHelper.read_file(args.input_file)
            print(f"{Colors.GREEN}Successfully read file: {args.input_file}{Colors.RESET}")
        print(f"{Colors.BLUE}Input prompt length: {len(input_prompt_content)} characters{Colors.RESET}")
    except (FileNotFoundError, IOError) as e:
        print(f"{Colors.RED}Error reading file: {e}{Colors.RESET}")
        sys.exit(1)
    
    # Step 2: Combine prompts
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{Colors.BLUE}🔄 Combining prompts")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    combined_prompt = prompt_refiner.combine_refinement_prompt(
        input_prompt_content, refinement_prompt_content
    )
    print(f"{Colors.BLUE}Combined prompt length: {len(combined_prompt)} characters{Colors.RESET}")
    
    # Step 3: Send to refinement model
    print(f"\n{Colors.YELLOW}{'='*60}")
    print(f"{Colors.YELLOW}🔄 Sending to refinement model: {refinement_model}")
    print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")
    refinement_response = llm_api.send(
        prompt=combined_prompt,
        model=refinement_model,
        max_tokens=args.max_tokens_refinement,
        temperature=refinement_temperature
    )
    print(f"{Colors.GREEN}Received refinement response: {len(refinement_response)} characters{Colors.RESET}")
    
    # Step 4: Clean the refined response
    print(f"\n{Colors.MAGENTA}{'='*60}")
    print(f"{Colors.MAGENTA}🔄 Cleaning refined response")
    print(f"{Colors.MAGENTA}{'='*60}{Colors.RESET}")
    cleaned_refined_prompt = prompt_refiner.clean_response(refinement_response)
    print(f"{Colors.GREEN}Cleaned refined prompt length: {len(cleaned_refined_prompt)} characters{Colors.RESET}")
    
    # Step 5: Send to output model
    print(f"\n{Colors.GREEN}{'='*60}")
    print(f"{Colors.GREEN}🔄 Sending to output model: {output_model}")
    print(f"{Colors.GREEN}{'='*60}{Colors.RESET}")
    final_response = llm_api.send(
        prompt=cleaned_refined_prompt,
        model=output_model,
        max_tokens=args.max_tokens_output,
        temperature=output_temperature,
        context=context
    )
    print(f"{Colors.GREEN}Received final response: {len(final_response)} characters{Colors.RESET}")
    
    # Write the final response to the output file if --output is provided
    if args.output:
        try:
            print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
            FileHelper.write_to_file(file_path=args.output, content=final_response)
            print(f"{Colors.GREEN}Final response saved to: {args.output}{Colors.RESET}")
        except IOError as e:
            print(f"{Colors.RED}Error writing to output file: {e}{Colors.RESET}")
            sys.exit(1)
    
    # Final success message
    print(f"\n{Colors.CYAN}{'='*60}")
    print(f"{Colors.CYAN}🎉 Process completed successfully! 🎉")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.GREEN}Final response length: {len(final_response)} characters{Colors.RESET}")
    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Process interrupted by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}Unexpected error: {str(e)}{Colors.RESET}")
        sys.exit(1)
