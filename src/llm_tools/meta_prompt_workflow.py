# This script defines the `MetaPromptWorkflow` class, which orchestrates a
# multi-stage process for generating and refining prompts using Large Language Models (LLMs).
# It supports generating initial topics, creating detailed execution prompts based on templates,
# refining these prompts for clarity and effectiveness, executing them with an LLM,
# and managing the output. This workflow is designed to automate and enhance
# the prompt engineering process.

from . import LLMApi, PromptRefiner, Colors, FileHelper, Config
from .output_printer import OutputPrinter
import os
import json
import time

class MetaPromptWorkflow:
    """
    Orchestrates a multi-step workflow for generating, refining, and executing LLM prompts.
    This class manages the flow from initial topic generation to final output,
    leveraging different LLM models for various stages of the process.
    """
    DEFAULT_MODEL = "qwen3-14b-128k" # Consider making this configurable or deriving from Config
  
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
        max_tokens: int = 20000, temperature: float = 0.7, verbose: bool = False):
        """
        Initializes the MetaPromptWorkflow.

        Args:
            api_endpoint (str): The API endpoint for the LLM server.
            api_key (str): The API key for the LLM server.
            topic_input_file (str, optional): Path to a file containing the initial topic.
                                              If None, a topic will be generated. Defaults to None.
            meta_prompt_generator_file (str, optional): Path to the prompt template for generating the initial topic.
                                                        Required if topic_input_file is None. Defaults to None.
            refinement_prompt_file (str, optional): Path to the prompt template for refining generated prompts. Defaults to None.
            prompt_generator_file (str, optional): Path to the prompt template for generating execution prompts. Defaults to None.
            output_directory (str, optional): Directory where generated outputs will be saved. Defaults to None.
            generator_llm_model (str, optional): The LLM model to use for generating execution prompts.
                                                 Defaults to Config.DEFAULT_MODEL.
            refinement_llm_model (str, optional): The LLM model to use for refining prompts.
                                                  Defaults to Config.DEFAULT_MODEL.
            execution_llm_model (str, optional): The LLM model to use for executing the final prompts.
                                                 Defaults to Config.DEFAULT_MODEL.
            meta_llm_model (str, optional): The LLM model to use for generating the initial topic (meta-prompt).
                                            Defaults to Config.DEFAULT_MODEL.
            max_tokens (int): Maximum tokens for LLM responses. Defaults to 20000.
            temperature (float): Temperature for LLM responses. Defaults to 0.7.
            verbose (bool): If True, enables verbose output. Defaults to False.
        """
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
        
        self.generator_llm_model = generator_llm_model if generator_llm_model else Config.DEFAULT_MODEL
        self.refinement_llm_model = refinement_llm_model if refinement_llm_model else Config.DEFAULT_MODEL
        self.execution_llm_model = execution_llm_model if execution_llm_model else Config.DEFAULT_MODEL
        self.meta_llm_model = meta_llm_model if meta_llm_model else Config.DEFAULT_MODEL
        
    def generate_or_set_topic(self) -> str:
        """
        Generates an initial topic using a meta-prompt or reads it from a file.

        Returns:
            str: The generated or read topic content.
        """
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
    
    def execute_prompt_generation(self) -> list[str]:
        """
        Generates a list of execution prompts based on a template and the initial topic.
        The generated prompts are expected to be in JSON format and are saved to a file.

        Returns:
            list[str]: A list of generated prompts.
        """
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
        
        json_path = os.path.join(self.output_directory, "generated_prompts.json")
        FileHelper.write_to_file(json_path, cleaned_json, self.verbose)
        
        return json.loads(cleaned_json)["prompts"]
    
    def refine_and_execute_prompt(self, execution_prompt: str, index: int) -> str:
        """
        Refines a given execution prompt and then executes it using an LLM.

        Args:
            execution_prompt (str): The prompt to be refined and executed.
            index (int): The index of the prompt (used for logging or naming).

        Returns:
            str: The final output from the LLM after executing the refined prompt.
        """
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
        
        final_output = self.llm_api.send(
            cleaned_refined,
            model=self.execution_llm_model,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        return final_output
    
    def run(self) -> None:
        """
        Executes the full meta-prompt workflow. This includes:
        1. Generating or setting the initial topic.
        2. Generating a set of execution prompts.
        3. Iterating through each generated prompt, refining it, and executing it with an LLM.
        4. Saving the final outputs to files in a timestamped directory.
        5. Reporting the total execution time.
        """
        self.output_directory = FileHelper.generate_postfixed_sub_directory_name(self.output_directory)
        start_time = time.time()
        
        OutputPrinter.print_header("🚀 Meta Prompt Generator 🚀", Colors.BRIGHT_CYAN, 60)
        
        self.generated_content = self.generate_or_set_topic()
        
        execution_prompts = self.execute_prompt_generation()
        
        created_files = []
        for idx, prompt in enumerate(execution_prompts):
            try:
                result = self.refine_and_execute_prompt(prompt, idx+1)
                
                output_filename = os.path.join(
                    self.output_directory,
                    f"output_{idx+1}_{self.execution_llm_model}.md"
                )
                output_filename = FileHelper.clean_name(output_filename)
                FileHelper.write_to_file(output_filename, result, self.verbose)
                created_files.append(output_filename)
            except Exception as e:
                OutputPrinter.print_error(f"Issue processing prompt {idx}: {str(e)}")
        
        end_time = time.time()
        total_seconds = round(end_time - start_time, 2)
        OutputPrinter.print_header("🎉 Workflow Completed! 🎉", Colors.BRIGHT_GREEN, 60)
        OutputPrinter.print_info(f"Total execution time: {total_seconds} seconds", Colors.BRIGHT_MAGENTA)
        
        if created_files:
            for f in created_files:
                OutputPrinter.print_file_created(f)
        else:
            OutputPrinter.print_warning("No output files generated")