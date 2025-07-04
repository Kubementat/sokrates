from .llm_api import LLMApi
from .prompt_refiner import PromptRefiner
from .colors import Colors
from .config import Config

"""
A class for orchestrating prompt refinement workflows.
"""
class RefinementWorkflow:
    def __init__(self, api_endpoint: str = Config.DEFAULT_API_ENDPOINT, 
        api_key: str = Config.DEFAULT_API_KEY, 
        model: str = Config.DEFAULT_MODEL, 
        max_tokens: int = 20000,
        temperature: float = 0.7,
        verbose: bool = False) -> None:
      self.llm_api = LLMApi(api_endpoint=api_endpoint, api_key=api_key, verbose=verbose)
      self.refiner = PromptRefiner(verbose=verbose)
      self.model = model
      self.max_tokens = max_tokens
      self.temperature = temperature
      self.verbose = verbose
      
    
    def refine_prompt(self, input_prompt: str, refinement_prompt: str) -> str:
      if self.verbose:
        print(f"{Colors.MAGENTA}Refining prompt:\n{Colors.RESET}")
        print(f"{Colors.MAGENTA}{input_prompt}\n{Colors.RESET}")
      combined_prompt = self.refiner.combine_refinement_prompt(input_prompt, refinement_prompt)
      response_content = self.llm_api.send(combined_prompt, model=self.model, max_tokens=self.max_tokens)
      processed_content = self.refiner.clean_response(response_content)

      # Format as markdown
      markdown_output = self.refiner.format_as_markdown(processed_content)
      if self.verbose:
        print(f"{Colors.MAGENTA}Processed response:\n{Colors.RESET}")
        print(f"{Colors.MAGENTA}{markdown_output}\n{Colors.RESET}")
      return markdown_output
    
    def refine_and_send_prompt(self, input_prompt: str, refinement_prompt: str, refinement_model: str = None, execution_model: str = None, refinement_temperature: float = None) -> str:
      if not refinement_model:
        refinement_model = self.model
      if not execution_model:
        execution_model = self.model
      if not refinement_temperature:
        refinement_temperature = self.temperature
      
      if self.verbose:
        print(f"{Colors.MAGENTA}Refining and sending prompt...\n{Colors.RESET}")
      refined_prompt = self.refine_prompt(input_prompt=input_prompt, refinement_prompt=refinement_prompt)
      
      if self.verbose:
        print(f"{Colors.MAGENTA}Sending refined prompt to model: {self.model_name}\n{Colors.RESET}")
      
      
      response_content = self.llm_api.send(refined_prompt, model=execution_model, 
        max_tokens=self.max_tokens, temperature=refinement_temperature)
      processed_content = self.refiner.clean_response(response_content)

      # Format as markdown
      markdown_output = self.refiner.format_as_markdown(processed_content)
      if self.verbose:
        print(f"{Colors.MAGENTA}Execution response:\n{Colors.RESET}")
        print(f"{Colors.MAGENTA}{markdown_output}\n{Colors.RESET}")
      return markdown_output
      
