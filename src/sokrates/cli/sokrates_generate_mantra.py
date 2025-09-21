#!/usr/bin/env python3
"""
Python Script to generate a daily mantra and practical call to action utilizing a LLM via REST Endpoint (OpenAI Compatible API)
"""
import argparse
from pathlib import Path

from sokrates.cli.colors import Colors
from sokrates.config import Config
from sokrates.workflows.refinement_workflow import RefinementWorkflow
from sokrates.cli.output_printer import OutputPrinter
from sokrates.cli.helper import Helper

def main():
    """Main function to handle command line arguments and orchestrate the process."""
    
    # Print beautiful header
    OutputPrinter.print_header("🤖 DAILY MANTRA GENERATOR 🌱", Colors.BRIGHT_CYAN, 60)
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Generates a daily mantra with a matching practical call to action',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '--provider',
        required=False,
        default=None,
        help="The provider to list models for."
    )
    
    parser.add_argument(
        '--generation-prompt-file', '-g',
        required=False,
        help='Path to a file containing with markdown files to add to the context'
    )
    
    parser.add_argument(
        '--api-endpoint',
        required=False,
        default=None,
        help="LLM server API endpoint."
    )
    
    parser.add_argument(
        '--api-key',
        default=None,
        help='API key for authentication (many local servers don\'t require this)'
    )
    
    parser.add_argument(
        '--model', '-m',
        default=None,
        help="A model name to use for the generation."
    )
    
    parser.add_argument(
        '--max-tokens', '-mt',
        type=int,
        default=4000,
        help='Maximum tokens in response (default: 4000)'
    )
    
    parser.add_argument(
        '--temperature', '-t',
        type=float,
        default=None,
        help='Temperature for response generation.'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output with debug information'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output filename to save the response (e.g., response.md)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    config = Helper.load_config()
    api_endpoint = Helper.get_provider_value('api_endpoint', config, args)
    api_key = Helper.get_provider_value('api_key', config, args)
    temperature = Helper.get_provider_value('temperature', config, args, 'default_temperature')
    model = Helper.get_provider_value('model', config, args, 'default_model')
    
    Helper.print_configuration_section(config=config, args=args)
    
    workflow = RefinementWorkflow(api_endpoint=api_endpoint, api_key=api_key, 
        model=model, temperature=temperature, max_tokens=args.max_tokens
    )
    
    context_files = [
        (config.get('prompts_directory') / 'context' / 'self-improvement-principles-v1.md').resolve()
    ]
    generated = workflow.generate_mantra(context_files=context_files)
    if args.verbose:
        OutputPrinter.print_info("context_files", context_files)

    OutputPrinter.print_section("✨ YOUR MANTRA FOR TODAY ✨\n", Colors.BRIGHT_MAGENTA, "═")
    print(f"{Colors.WHITE}{generated}{Colors.RESET}")
    
    
if __name__ == "__main__":
    main()
    