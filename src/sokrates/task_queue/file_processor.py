#!/usr/bin/env python3
"""
File Processor Module

This module provides functionality for processing file contents through
the existing prompt refinement and execution pipeline.
"""

import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from sokrates.file_helper import FileHelper
from sokrates.prompt_refiner import PromptRefiner
from sokrates.llm_api import LLMApi


class FileProcessor:
    """
    Processes file contents through the prompt refinement and execution pipeline.
    
    This class reads file contents, refines them using the existing PromptRefiner,
    and executes them via the LLM API, following the same workflow as the
    existing task processing system.
    """

    DEFAULT_MAX_TOKENS_REFINEMENT = 6000
    DEFAULT_MAX_TOKENS_EXECUTION = 16*1024
    
    def __init__(self, config, logger: logging.Logger = None):
        """
        Initialize the FileProcessor.
        
        Args:
            config: Config instance with API settings
            logger: Logger instance for logging events
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize components
        self.refiner = PromptRefiner()

        default_provider = config.get_default_provider()
        self.llm_api = LLMApi(
            api_endpoint=default_provider.get('api_endpoint'),
            api_key=default_provider.get('api_key')
        )
        
        # Output directory for file processing results
        self.output_dir = config.get('home_path') / "tasks" / "results"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load refinement prompt
        self.refinement_prompt_path = config.get('prompts_directory') / "refine-prompt.md"
        self.refinement_prompt = self._load_refinement_prompt()
        
    
    def _load_refinement_prompt(self) -> str:
        """Load the refinement prompt from file."""
        try:
            if self.refinement_prompt_path.exists():
                return FileHelper.read_file(str(self.refinement_prompt_path))
            else:
                self.logger.warning(f"Refinement prompt file not found at {self.refinement_prompt_path}")
                return self._get_default_refinement_prompt()
        except Exception as e:
            self.logger.error(f"Error loading refinement prompt: {e}")
            return self._get_default_refinement_prompt()
    
    def _get_default_refinement_prompt(self) -> str:
        """Get a default refinement prompt if file is not available."""
        return """Please refine and improve the following prompt to make it more effective for LLM processing:

{input_prompt}

Focus on:
1. Clarity and specificity
2. Proper structure and formatting
3. Context and background information
4. Desired output format

Refined prompt:"""
    
    def _read_and_validate_file(self, file_path: str) -> tuple:
       """Read and validate file content and metadata."""
       try:
           self.logger.debug(f"Reading and validating file: {file_path}")
           file_path_obj = Path(file_path)
           
           # Validate file exists and is readable
           if not file_path_obj.exists():
               error_msg = f"File does not exist: {file_path}"
               self.logger.error(error_msg)
               return None, None, error_msg
               
           # Read file with frontmatter
           metadata_result = FileHelper.read_file_with_frontmatter(file_path)
           file_content = metadata_result['content']
           metadata = metadata_result['metadata']
           
           # Validate file content
           if not file_content:
               error_msg = "File is empty or could not be read"
               self.logger.error(error_msg)
               return None, None, error_msg
               
           self.logger.info(f"Successfully read file content: {len(file_content)} characters")
           
           return file_content, metadata, None
       except Exception as e:
           error_msg = f"Error reading and validating file '{file_path}': {str(e)}"
           self.logger.error(error_msg)
           return None, None, error_msg
   
    def _resolve_configuration(self, metadata) -> tuple:
       """Resolve provider configuration from metadata."""
       try:
           self.logger.debug("Resolving configuration from metadata")
           # Determine configuration based on metadata
           provider_name = metadata.get('provider')
           model_name = metadata.get('model')
           temperature = metadata.get('temperature')
           refinement_enabled = metadata.get('refinement', False)  # Default to False as per feature spec
           
           self.logger.info(f"Read frontmatter configuration from file: provider={provider_name}, model={model_name}, temperature={temperature}, refinement={refinement_enabled}")
           
           # Override default configuration with metadata values if provided
           provider_config = self.config.get_default_provider()
           if provider_name:
               try:
                   provider_config = self.config.get_provider(provider_name)
               except ValueError as e:
                   self.logger.warning(f"Invalid provider '{provider_name}' in metadata, using default provider: {e}")
           
           self.logger.debug("Successfully resolved configuration")
           return provider_config, model_name, temperature, refinement_enabled
       except Exception as e:
           error_msg = f"Error resolving configuration from metadata: {str(e)}"
           self.logger.error(error_msg)
           # Return defaults in case of error
           provider_config = self.config.get_default_provider()
           self.logger.debug("Returning default configuration due to error")
           return provider_config, None, None, False
   
    def _refine_prompt_if_enabled(self, file_content: str, provider_config: Dict[str, Any],
                                 model_name: Optional[str], temperature: Optional[float], refinement_enabled: bool) -> Optional[str]:
       """Refine prompt if enabled in metadata."""
       refined_prompt = None
       if refinement_enabled:
           self.logger.info(f"Refining the prompt for file...")
           self.logger.debug("Calling _refine_prompt_with_config")
           refined_prompt = self._refine_prompt_with_config(file_content, provider_config, model_name, temperature)
           if refined_prompt:
               self.logger.info("Prompt refinement completed successfully")
           else:
               self.logger.error("Prompt refinement failed")
       else:
           self.logger.info(f"Refinement disabled. Skipping refinement!")
           # If refinement is disabled, use content directly as prompt
           refined_prompt = file_content
       
       return refined_prompt
   
   
    def _execute_refined_prompt(self, refined_prompt: str, provider_config: Dict[str, Any],
                               model_name: str, temperature: float) -> Optional[str]:
       """Execute the refined prompt."""
       self.logger.info(f"Executing the refined prompt...")
       execution_result = self._execute_prompt_with_provider_config(refined_prompt, provider_config, model_name, temperature)
       return execution_result
   
    def _save_and_cleanup(self, result: Dict[str, Any], file_path: str) -> Path:
       """Save results and cleanup original file."""
       self.logger.debug("Saving results and cleaning up")
       # Save results to file
       output_file = self._save_results(result)
       result["output_file"] = str(output_file)
       self.logger.info(f"Saved the results -> {output_file}")
       
       # Remove original file in input directory
       self.logger.info(f"Deleting the original input file: {file_path} ...")
       FileHelper.delete_file(file_path=file_path)
       self.logger.debug("File cleanup completed")
       
       return output_file
   
    def process_file(self, file_path: str) -> Dict[str, Any]:
       """
       Process a file through the refinement and execution pipeline.
       
       Args:
           file_path: Path to the file to process
           
       Returns:
           Dict containing processing results and metadata
       """
       # Add input validation at the beginning
       if not file_path or not isinstance(file_path, str):
           raise ValueError("Invalid file path provided")
       
       # Validate file exists and is readable
       file_path_obj = Path(file_path)
       if not file_path_obj.exists():
           raise FileNotFoundError(f"File does not exist: {file_path}")
           
       start_time = time.time()
       file_path_obj = Path(file_path)
       
       self.logger.info(f"Starting file processing: {file_path}")
       
       result = {
           "file_path": file_path,
           "file_name": file_path_obj.name,
           "file_size": file_path_obj.stat().st_size if file_path_obj.exists() else 0,
           "processing_start_time": datetime.now().isoformat(),
           "status": "started",
           "error": None,
           "refined_prompt": None,
           "execution_result": None,
           "output_file": None,
           "processing_duration": None
       }
       
       try:
           # Step 1: Read and validate file content
           file_content, metadata, error = self._read_and_validate_file(file_path)
           if error:
               result["status"] = "failed"
               result["error"] = error
               return result
           
           # Step 2: Resolve configuration from metadata
           provider_config, model_name, temperature, refinement_enabled = self._resolve_configuration(metadata)
           
           # Step 3: Refine the prompt (only if refinement is enabled in metadata)
           refined_prompt = self._refine_prompt_if_enabled(file_content, provider_config, model_name, temperature, refinement_enabled)
           if not refined_prompt:
               result["status"] = "failed"
               result["error"] = "Prompt refinement failed"
               return result
               
           result["refined_prompt"] = refined_prompt
           self.logger.info(f"Refined prompt: {len(refined_prompt)} characters")
           
           # Step 4: Execute the refined prompt
           execution_result = self._execute_prompt_with_provider_config(refined_prompt, provider_config, model_name, temperature)
           if not execution_result:
               result["status"] = "failed"
               result["error"] = "Prompt execution failed"
               return result
               
           result["execution_result"] = execution_result
           self.logger.info(f"Execution result: {len(execution_result)} characters")
           
           # Update processing duration
           processing_duration = time.time() - start_time
           result["processing_duration"] = processing_duration

           # Step 5: Save results to file and cleanup
           # Pass the original file content to avoid reading it again in _format_output_content
           result["original_file_content"] = file_content
           result["original_file_metadata"] = metadata
           output_file = self._save_and_cleanup(result, file_path)
           
           # Update final status
           result["status"] = "completed"
           
           self.logger.info(f"File processing completed successfully in {processing_duration:.2f}s")
           self.logger.info(f"Results saved to: {output_file}")
           
       except Exception as e:
           result["status"] = "failed"
           result["error"] = str(e)
           self.logger.error(f"File processing failed: {e}")
           
       finally:
           result["processing_end_time"] = datetime.now().isoformat()
           
       return result
    
    
    def _refine_prompt_with_config(self, input_prompt: str, provider_config: Dict[str, Any], model_name: Optional[str] = None, temperature: Optional[float] = None) -> Optional[str]:
       """
       Refine the input prompt using the existing refinement workflow with custom configuration.
       
       Args:
           input_prompt: The raw prompt from the file
           provider_config: Provider configuration dictionary
           model_name: Specific model name to use (optional)
           temperature: Specific temperature to use (optional)
           
       Returns:
           Refined prompt, or None if refinement failed
       """
       try:
           # Use the existing PromptRefiner to combine and refine the prompt
           combined_prompt = self.refiner.combine_refinement_prompt(
               input_prompt=input_prompt,
               refinement_prompt=self.refinement_prompt
           )
           
           # Send to LLM for refinement with custom configuration
           model_to_use = model_name or provider_config.get('default_model')
           temp_to_use = temperature if temperature is not None else provider_config.get('default_temperature')
           
           self.logger.info(f"Refinement configuration: model={model_to_use} , temperature={temp_to_use}")
           refined_response = self.llm_api.send(
               prompt=combined_prompt,
               model=model_to_use,
               max_tokens=self.DEFAULT_MAX_TOKENS_REFINEMENT,
               temperature=temp_to_use
           )
           
           # Clean the response
           cleaned_response = self.refiner.clean_response(refined_response)
           
           # Format as markdown
           refined_prompt = self.refiner.format_as_markdown(cleaned_response)
           
           return refined_prompt
           
       except Exception as e:
           error_msg = f"Error refining prompt: {e}"
           self.logger.error(error_msg)
           return None
    
    
    def _execute_prompt_with_provider_config(self, refined_prompt: str, provider_config: Dict[str, Any], model_name: Optional[str] = None, temperature: Optional[float] = None) -> Optional[str]:
       """
       Execute the refined prompt using the LLM API with specific provider configuration.
       
       Args:
           refined_prompt: The refined prompt to execute
           provider_config: Provider configuration dictionary
           model_name: Specific model name to use (optional)
           temperature: Specific temperature to use (optional)
           
       Returns:
           Execution result, or None if execution failed
       """
       try:
           self.logger.debug("Executing prompt with LLM API")
           # Send refined prompt to LLM for execution
           model_to_use = model_name or provider_config.get('default_model')
           temp_to_use = temperature if temperature is not None else provider_config.get('default_temperature')
           
           self.logger.info(f"Execution configuration: model={model_to_use} , temperature={temp_to_use}")
           execution_result = self.llm_api.send(
               prompt=refined_prompt,
               model=model_to_use,
               max_tokens=self.DEFAULT_MAX_TOKENS_EXECUTION,
               temperature=temp_to_use
           )

           self.logger.info(f"Execution result content length: {len(execution_result)}")
           
           # Clean and format the response
           cleaned_result = self.refiner.clean_response(execution_result)
           formatted_result = self.refiner.format_as_markdown(cleaned_result)
           
           self.logger.info(f"Execution result clean formatted content length: {len(formatted_result)}")
           self.logger.debug("Prompt execution completed successfully")
           
           return formatted_result
           
       except Exception as e:
           error_msg = f"Error executing prompt: {e}"
           self.logger.error(error_msg)
           return None
    
    
    def _save_results(self, result: Dict[str, Any]) -> Path:
        """
        Save processing results to a file.
        
        Args:
            result: Dictionary containing processing results
            
        Returns:
            Path to the output file
        """
        try:
            # Generate output filename
            file_name = result["file_name"]
            base_name = Path(file_name).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{timestamp}_{base_name}_processed.md"
            output_path = self.output_dir / output_filename

            self.logger.info(f"Result file target path: {str(output_path)}")
            
            # Create the output content
            output_content = self._format_output_content(result)
            
            # Write to file
            FileHelper.write_to_file(str(output_path), output_content)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")
            self.logger.exception(e)
            # Return a fallback path
            return self.output_dir / "error_saving_results.md"
    
    def _format_output_content(self, result: Dict[str, Any]) -> str:
       """
       Format the processing results for output.
       
       Args:
           result: Dictionary containing processing results
           
       Returns:
           Formatted content string
       """
       self.logger.info("Formatting result output ...")

       # Safely extract values with defaults to avoid None formatting issues
       file_path = result.get('file_path') or 'Unknown'
       file_size = result.get('file_size', 0) or 0
       
       # Handle processing duration which could be None
       processing_duration_str = f"{result.get('processing_duration'):.2f}"
       processing_start_time = result.get('processing_start_time') or 'Unknown'
       refined_prompt = result.get('refined_prompt')
       execution_result = result.get('execution_result')
       
       error = result.get('error')
       full_error_section = ""
       if error:
           full_error_section = f"## Error Information\n{error}"
       
       # Use the original file content that was passed in to avoid reading it again
       original_content = result.get('original_file_content', '')
       if not original_content:
           # Fallback to reading the file if needed
           try:
               original_content = FileHelper.read_file(file_path)
           except Exception as e:
               self.logger.warning(f"Could not read original file for output: {e}")
               original_content = "Original content could not be retrieved"
    
       processing_configuration = result.get('original_file_metadata', '')

       content = f"""# File Processing Results

## File Information
- **Original File**: `{file_path}`
- **File Size**: {file_size} bytes
- **Processing Start Time**: {processing_start_time}
- **Processing Duration**: {processing_duration_str} seconds

## Processing Configuration
```
{processing_configuration}
```

## Original Content
```
{original_content}
```

## Refined Prompt
```
{refined_prompt or 'Refinement failed'}
```

## Execution Result
{execution_result or 'Execution failed'}

{full_error_section}
"""
       
       return content