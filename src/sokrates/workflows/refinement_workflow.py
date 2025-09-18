# This script defines the `RefinementWorkflow` class, which orchestrates
# prompt refinement and execution processes. It integrates with `LLMApi`
# for interacting with Large Language Models and `PromptRefiner` for
# cleaning and formatting LLM responses. This class provides methods
# for refining input prompts, sending them to LLMs for execution, and
# generating specific content like "mantras" based on provided context.

from typing import List, Optional
from pathlib import Path
import logging
from sokrates.llm_api import LLMApi
from sokrates.prompt_refiner import PromptRefiner
from sokrates.file_helper import FileHelper

class RefinementWorkflow:
    """
    Orchestrates prompt refinement and execution workflows.

    This class integrates with LLM API for model interaction and
    PromptRefiner for prompt processing and response cleaning.
    """

    DEFAULT_CONTEXT_FILES = [
      Path(__file__).parent / "prompts" / "context" / "self-improvement-principles-v1.md"
    ]
    DEFAULT_TASK_FILEPATH = Path(__file__).parent / "prompts" / "generate-mantra-v1.md"

    def __init__(self, api_endpoint: str, 
        api_key: str, 
        model: str, 
        max_tokens: int = 20000,
        temperature: float = 0.7) -> None:
      """
      Initializes the RefinementWorkflow.

      Args:
          api_endpoint (str): The API endpoint for the LLM. 
          api_key (str): The API key for the LLM. 
          model (str): The default LLM model to use.
          max_tokens (int): The maximum number of tokens for LLM responses. Defaults to 20000.
          temperature (float): The sampling temperature for LLM responses. Defaults to 0.7.
      """
      self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
      self.llm_api = LLMApi(api_endpoint=api_endpoint, api_key=api_key)
      self.refiner = PromptRefiner()
      self.model = model
      self.max_tokens = max_tokens
      self.temperature = temperature

    def refine_prompt(self, input_prompt: str, refinement_prompt: str, context: List[str]=None) -> str:
      """
      Refines an input prompt using a specified refinement prompt and an LLM.

      Args:
          input_prompt (str): The initial prompt to be refined.
          refinement_prompt (str): The prompt containing instructions for refinement.
          context (List[str], optional): additional context to include in the refinement prompt

      Returns:
          str: The refined and formatted prompt as a Markdown string.
      """
      self.logger.debug(f"Refining prompt: {input_prompt}")

      combined_prompt = self.refiner.combine_refinement_prompt(input_prompt, refinement_prompt)
      response_content = self.llm_api.send(combined_prompt, model=self.model, max_tokens=self.max_tokens, context=context)
      processed_content = self.refiner.clean_response(response_content)

      # Format as markdown
      markdown_output = self.refiner.format_as_markdown(processed_content)
      self.logger.debug(f"Processed response: {markdown_output}")
      return markdown_output
    
    def refine_and_send_prompt(self, 
          input_prompt: str, refinement_prompt: str, 
          refinement_model: str = None,
          refinement_temperature: float = None,
          execution_model: str = None,
          max_tokens: int = None
          ) -> str:
      """
      Refines an input prompt and then sends the refined prompt to an LLM for execution.

      Args:
          input_prompt (str): The initial prompt to be refined.
          refinement_prompt (str): The prompt containing instructions for refinement.
          refinement_model (str, optional): The model to use for refinement. Defaults to self.model.
          execution_model (str, optional): The model to use for execution. Defaults to self.model.
          refinement_temperature (float, optional): The temperature for refinement. Defaults to self.temperature.

      Returns:
          str: The executed response as a Markdown string.
      """
      if not refinement_model:
        refinement_model = self.model
      if not execution_model:
        execution_model = self.model
      if not refinement_temperature:
        refinement_temperature = self.temperature
      if not max_tokens:
        max_tokens = self.max_tokens
      
      self.logger.info("Refining and sending prompt...")
      refined_prompt = self.refine_prompt(input_prompt=input_prompt, refinement_prompt=refinement_prompt)
      
      self.logger.info(f"Sending refined prompt to model: {execution_model}")
      
      response_content = self.llm_api.send(refined_prompt, model=execution_model, 
          temperature=refinement_temperature, max_tokens=max_tokens)
      processed_content = self.refiner.clean_response(response_content)

      # Format as markdown
      markdown_output = self.refiner.format_as_markdown(processed_content)
      self.logger.debug(f"Execution response: {markdown_output}")
      return markdown_output
    
    def breakdown_task(self, task: str, context: List[str] = None):
      """
      Breaks down a task into sub-tasks using LLM refinement.

      Args:
          task (str): The main task to be broken down.
          model (str): The LLM model to use for breakdown.
          context (List[str], optional): Additional context to include in the breakdown process.

      Returns:
          str: The breakdown of the task as a Markdown string.
      """
      breakdown_instructions_filepath = Path(f"{Path(__file__).parent.parent.resolve()}/prompts/breakdown-v1.md").resolve()
      breakdown_instructions = FileHelper.read_file(breakdown_instructions_filepath)
      
      result = self.refine_prompt(input_prompt=task, refinement_prompt=breakdown_instructions, context=context)
      return result
    
    def generate_mantra(self, context_files: Optional[List[str] | List[Path]] = None, task_file_path: Optional[str|Path] = None) -> str:
      """
      Generates a "mantra" based on provided context and a task file.

      Args:
          context_files (List[str], optional): A list of file paths containing context for mantra generation.
                                               Defaults to a specific self-improvement principles file.
          task_file_path (str, optional): The file path containing the task prompt for mantra generation.
                                          Defaults to a specific generate-mantra file.

      Returns:
          str: The generated mantra as a Markdown string.
      """
      context_files = context_files or self.DEFAULT_CONTEXT_FILES
      task_file_path = task_file_path or self.DEFAULT_TASK_FILEPATH
      
      task = FileHelper.read_file(file_path=task_file_path)
      context = FileHelper.combine_files(file_paths=context_files)
      self.logger.debug(f"Context: {context}")
      
      combined_prompt = self.refiner.combine_refinement_prompt(task, context)
      response_content = self.llm_api.send(combined_prompt, model=self.model, max_tokens=self.max_tokens)
      processed_content = self.refiner.clean_response(response_content)

      # Format as markdown
      markdown_output = self.refiner.format_as_markdown(processed_content)
      self.logger.debug(f"Processed response: {markdown_output}")
      return markdown_output
