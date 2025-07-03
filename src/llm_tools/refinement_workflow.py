from .llm_api import LLMApi
from .prompt_refiner import PromptRefiner
from .colors import Colors

class RefinementWorkflow:
    def __init__(self, api_endpoint='http://localhost:1234', api_key='notrequired', model='qwen/qwen3-8b', max_tokens=20000, verbose=False):
      self.llm_api = LLMApi(api_endpoint=api_endpoint, api_key=api_key, verbose=verbose)
      self.refiner = PromptRefiner(verbose=verbose)
      self.model = model
      self.max_tokens = max_tokens
      self.verbose = verbose
      
    
    def refine_prompt(self, input_prompt, refinement_prompt) -> str:
      if self.verbose:
        print(f"{Colors.MAGENTA}Refining prompt:\n{Colors.RESET}")
        print(f"{Colors.MAGENTA}{input_prompt}\n{Colors.RESET}")
      breakpoint()
      combined_prompt = self.refiner.combine_refinement_prompt(input_prompt, refinement_prompt)
      response_content = self.llm_api.send(combined_prompt, model=self.model, max_tokens=self.max_tokens)
      processed_content = self.refiner.clean_response(response_content)

      # Format as markdown
      markdown_output = self.refiner.format_as_markdown(processed_content)
      return markdown_output