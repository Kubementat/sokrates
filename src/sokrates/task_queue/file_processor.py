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
        self.refiner = PromptRefiner(verbose=False)
        self.llm_api = LLMApi(
            api_endpoint=config.api_endpoint,
            api_key=config.api_key
        )
        
        # Output directory for file processing results
        self.output_dir = Path(config.home_path) / "tasks" / "results"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load refinement prompt
        self.refinement_prompt_path = Path(config.prompts_directory) / "refine-prompt.md"
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
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a file through the refinement and execution pipeline.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dict containing processing results and metadata
        """
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
            # Step 1: Read file content
            file_content = self._read_file_content(file_path)
            if not file_content:
                result["status"] = "failed"
                result["error"] = "File is empty or could not be read"
                return result
                
            self.logger.info(f"Read file content: {len(file_content)} characters")
            
            # Step 2: Refine the prompt
            self.logger.info(f"Refining the prompt for file: {file_path} ...")
            refined_prompt = self._refine_prompt(file_content)
            if not refined_prompt:
                result["status"] = "failed"
                result["error"] = "Prompt refinement failed"
                return result
                
            result["refined_prompt"] = refined_prompt
            self.logger.info(f"Refined prompt: {len(refined_prompt)} characters")
            
            # Step 3: Execute the refined prompt
            self.logger.info(f"Executing the refined prompt for file: {file_path} ...")
            execution_result = self._execute_prompt(refined_prompt)
            if not execution_result:
                result["status"] = "failed"
                result["error"] = "Prompt execution failed"
                return result
                
            result["execution_result"] = execution_result
            self.logger.info(f"Execution result: {len(execution_result)} characters")
            
            # update processing duration
            processing_duration = time.time() - start_time
            result["processing_duration"] = processing_duration

            # Step 4: Save results to file
            output_file = self._save_results(result)
            result["output_file"] = str(output_file)
            self.logger.info(f"Saved the results for file: {file_path} -> {output_file}")
            
            # Update final status
            result["status"] = "completed"

            # remove original file in input directory
            self.logger.info(f"Deleting the original input file: {file_path} ...")
            FileHelper.delete_file(file_path=file_path)
            
            self.logger.info(f"File processing completed successfully in {processing_duration:.2f}s")
            self.logger.info(f"Results saved to: {output_file}")
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self.logger.error(f"File processing failed: {e}")
            
        finally:
            result["processing_end_time"] = datetime.now().isoformat()
            
        return result
    
    def _read_file_content(self, file_path: str) -> Optional[str]:
        """
        Read content from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as string, or None if reading failed
        """
        try:
            file_path_obj = Path(file_path)
            
            # Check if file exists and is readable
            if not file_path_obj.exists():
                self.logger.error(f"File does not exist: {file_path}")
                return None
                
            if not file_path_obj.is_file():
                self.logger.error(f"Path is not a file: {file_path}")
                return None
                
            # Read file content
            content = FileHelper.read_file(str(file_path_obj))
            
            if not content or not content.strip():
                self.logger.warning(f"File is empty: {file_path}")
                return None
                
            return content.strip()
            
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    def _refine_prompt(self, input_prompt: str) -> Optional[str]:
        """
        Refine the input prompt using the existing refinement workflow.
        
        Args:
            input_prompt: The raw prompt from the file
            
        Returns:
            Refined prompt, or None if refinement failed
        """
        try:
            # Use the existing PromptRefiner to combine and refine the prompt
            combined_prompt = self.refiner.combine_refinement_prompt(
                input_prompt=input_prompt,
                refinement_prompt=self.refinement_prompt
            )
            
            # Send to LLM for refinement
            refined_response = self.llm_api.send(
                prompt=combined_prompt,
                model=self.config.default_model,
                max_tokens=4000,
                temperature=0.7
            )
            
            # Clean the response
            cleaned_response = self.refiner.clean_response(refined_response)
            
            # Format as markdown
            refined_prompt = self.refiner.format_as_markdown(cleaned_response)
            
            return refined_prompt
            
        except Exception as e:
            self.logger.error(f"Error refining prompt: {e}")
            return None
    
    def _execute_prompt(self, refined_prompt: str) -> Optional[str]:
        """
        Execute the refined prompt using the LLM API.
        
        Args:
            refined_prompt: The refined prompt to execute
            
        Returns:
            Execution result, or None if execution failed
        """
        try:
            # Send refined prompt to LLM for execution
            execution_result = self.llm_api.send(
                prompt=refined_prompt,
                model=self.config.default_model,
                max_tokens=8000,
                temperature=self.config.default_model_temperature
            )
            
            # Clean and format the response
            cleaned_result = self.refiner.clean_response(execution_result)
            formatted_result = self.refiner.format_as_markdown(cleaned_result)
            
            return formatted_result
            
        except Exception as e:
            self.logger.error(f"Error executing prompt: {e}")
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
        result.get('status') or 'Unknown'
        
        # Handle processing duration which could be None
        processing_duration_str = f"{result.get('processing_duration'):.2f}"
        processing_start_time = result.get('processing_start_time') or 'Unknown'
        refined_prompt = result.get('refined_prompt')
        execution_result = result.get('execution_result')
        
        error = result.get('error')
        full_error_section = ""
        if error:
            full_error_section = f"## Error Information\n{error}"
        original_content = FileHelper.read_file(file_path)
        
        content = f"""# File Processing Results

## File Information
- **Original File**: `{file_path}`
- **File Size**: {file_size} bytes
- **Processing Start Time**: {processing_start_time}
- **Processing Duration**: {processing_duration_str} seconds
 
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
    
    def get_output_directory(self) -> Path:
        """Get the output directory for file processing results."""
        return self.output_dir
    
    def get_processed_files_count(self) -> int:
        """Get the number of processed files in the output directory."""
        try:
            return len(list(self.output_dir.glob("*.md")))
        except Exception:
            return 0