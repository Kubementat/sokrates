from . import LLMApi, PromptRefiner, Colors, FileHelper
import os
import json
import time

class MetaPromptWorkflow:
    DEFAULT_MODEL = "qwen3-14b-128k"
  
    def __init__(self, api_endpoint: str, api_key: str,
        topic_input_file: str = None,
        meta_prompt_generator_file : str = None, 
        refinement_prompt_file: str = None,
        prompt_generator_file: str = None,
        output_directory: str = None,
        generator_llm_model: str = None,
        refinement_llm_model: str = None,
        execution_llm_model: str = None,
        meta_llm_model: str = None,
        max_tokens= 20000, temperature= 0.7, verbose: bool = False):
        # Initialize API with configured values unless overridden by CLI args
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.llm_api = LLMApi(api_endpoint=api_endpoint, 
                              api_key=api_key,
                              verbose=verbose)
        self.prompt_refiner = PromptRefiner(verbose=verbose)
        self.topic_input_file = topic_input_file
        self.meta_prompt_generator_file = meta_prompt_generator_file
        self.refinement_prompt_file = refinement_prompt_file
        self.prompt_generator_file = prompt_generator_file
        self.output_directory = output_directory
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.verbose = verbose
        
        self.generator_llm_model = generator_llm_model
        if not self.generator_llm_model:
          self.generator_llm_model = self.DEFAULT_MODEL
        
        self.refinement_llm_model = refinement_llm_model
        if not self.refinement_llm_model:
          self.refinement_llm_model = self.DEFAULT_MODEL
          
        self.execution_llm_model = execution_llm_model
        if not self.execution_llm_model:
          self.execution_llm_model = self.DEFAULT_MODEL
          
        self.meta_llm_model = meta_llm_model
        if not self.meta_llm_model:
          self.meta_llm_model = self.DEFAULT_MODEL
        
    def generate_or_set_topic(self):
        # Decide between topic input file or meta prompt generation
        if self.topic_input_file:
            return FileHelper.read_file(self.topic_input_file, self.verbose)
            
        else:
            meta_prompt_content = FileHelper.read_file(self.meta_prompt_generator_file, self.verbose)
            response = self.llm_api.send(
                prompt=meta_prompt_content,
                model=self.meta_llm_model,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return self.prompt_refiner.clean_response(response)
    
    def execute_prompt_generation(self):
        # Get the base template for generating execution prompts
        prompt_generator_template = FileHelper.read_file(self.prompt_generator_file, self.verbose)
        
        combined_prompt = f"{prompt_generator_template}\n{self.generated_content}"
        
        json_response = self.llm_api.send(
            prompt=combined_prompt,
            model=self.generator_llm_model,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        cleaned_json = self.prompt_refiner.clean_response(json_response)
        cleaned_json = self.prompt_refiner.clean_response_from_markdown(cleaned_json)
        
        # Save intermediate JSON to file
        json_path = os.path.join(self.output_directory, "generated_prompts.json")
        FileHelper.write_to_file(json_path, cleaned_json, self.verbose)
        
        return json.loads(cleaned_json)["prompts"]
    
    def refine_and_execute_prompt(self, execution_prompt, index):
        # Refinement step
        combined_refinement = self.prompt_refiner.combine_refinement_prompt(
            execution_prompt,
            FileHelper.read_file(self.refinement_prompt_file, self.verbose)
        )
        
        refined_prompt = self.llm_api.send(
            combined_refinement,
            model=self.refinement_llm_model,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        cleaned_refined = self.prompt_refiner.clean_response(refined_prompt)
        
        # Execution step
        final_output = self.llm_api.send(
            cleaned_refined,
            model=self.execution_llm_model,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        return final_output
    
    def run(self):
        # setting output directory to datetime sub-directory
        self.output_directory = FileHelper.generate_postfixed_sub_directory_name(self.output_directory)
        start_time = time.time()
        
        self.print_header("🚀 Meta Prompt Generator 🚀", Colors.BRIGHT_CYAN, 60)
        
        self.generated_content = self.generate_or_set_topic()
        
        # Process the prompts generation phase
        execution_prompts = self.execute_prompt_generation()
        
        created_files = []
        for idx, prompt in enumerate(execution_prompts):
            try:
                result = self.refine_and_execute_prompt(prompt, idx+1)
                
                output_filename = os.path.join(
                    self.output_directory,
                    f"output_{idx+1}_{self.execution_llm_model}.md"
                )
                FileHelper.write_to_file(output_filename, result, self.verbose)
                created_files.append(output_filename)
            except Exception as e:
                self.print_error(f"Issue processing prompt {idx}: {str(e)}")
        
        # Final reporting
        end_time = time.time()
        total_seconds = round(end_time - start_time, 2)
        self.print_header("🎉 Workflow Completed! 🎉", Colors.BRIGHT_GREEN, 60)
        self.print_info(f"Total execution time: {total_seconds} seconds", Colors.BRIGHT_MAGENTA)
        
        if created_files:
            for f in created_files:
                self.print_file_created(f)
        else:
            self.print_warning("No output files generated")

    def print_header(self, title, color=Colors.BRIGHT_CYAN, width=60):
      """Print a beautiful header with decorative borders"""
      border = "═" * width
      print(f"\n{color}{Colors.BOLD}╔{border}╗{Colors.RESET}")
      print(f"{color}{Colors.BOLD}║{title.center(width)}║{Colors.RESET}")
      print(f"{color}{Colors.BOLD}╚{border}╝{Colors.RESET}\n")

    def print_section(self, title, color=Colors.BRIGHT_BLUE, char="─"):
        """Print a section separator"""
        print(f"\n{color}{Colors.BOLD}{char * 50}{Colors.RESET}")
        print(f"{color}{Colors.BOLD} {title}{Colors.RESET}")
        print(f"{color}{Colors.BOLD}{char * 50}{Colors.RESET}")

    def print_info(self, label, value, label_color=Colors.BRIGHT_GREEN, value_color=Colors.WHITE):
        """Print formatted info with colored labels"""
        print(f"{label_color}{Colors.BOLD}{label}:{Colors.RESET} {value_color}{value}{Colors.RESET}")

    def print_success(self, message):
        """Print success message"""
        print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}✓ {message}{Colors.RESET}")

    def print_warning(self, message):
        """Print warning message"""
        print(f"{Colors.BRIGHT_YELLOW}{Colors.BOLD}⚠ {message}{Colors.RESET}")

    def print_error(self, message):
        """Print error message"""
        print(f"{Colors.BRIGHT_RED}{Colors.BOLD}✗ {message}{Colors.RESET}")

    def print_progress(self, message):
        """Print progress message"""
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}⟳ {message}{Colors.RESET}")

    def print_file_created(self, filename):
        """Print file creation message"""
        print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}📄 Created: {Colors.RESET}{Colors.CYAN}{filename}{Colors.RESET}")
