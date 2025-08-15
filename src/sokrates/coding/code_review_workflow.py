"""
Code Review Workflow Module

This module implements the core workflow for analyzing Python code and generating 
automated code reviews using LLMs. It leverages the existing PythonAnalyzer infrastructure
to extract structured code information, then applies appropriate prompt templates based on
the review type to generate comprehensive feedback.
"""

from ..coding.python_analyzer import PythonAnalyzer
from ..llm_api import LLMApi
from ..file_helper import FileHelper
from ..prompt_refiner import PromptRefiner
import os
import json
from typing import List, Dict, Any

CODE_REVIEW_TYPE_ALL = "all"

class CodeReviewWorkflow:
    """
    A workflow class for performing code reviews on Python files using LLMs.
    
    This class orchestrates the process of analyzing Python code with PythonAnalyzer,
    preparing structured input data, and sending prompts to LLM APIs for review generation.
    """
    
    REVIEW_TYPES = [
        'style',
        'security',
        'performance',
        'quality'
    ]
    
    PROMPT_TEMPLATES = {
        "style": "src/sokrates/prompts/coding/style_review.md",
        "security": "src/sokrates/prompts/coding/security_review.md",
        "performance": "src/sokrates/prompts/coding/performance_review.md",
        "quality": "src/sokrates/prompts/coding/code_quality_review.md"
    }

    def __init__(self, verbose: bool = False, api_endpoint: str = None, api_key: str = None):
        """
        Initialize the CodeReviewWorkflow.
        
        Args:
            verbose (bool): Enable verbose output
            api_endpoint (str): Custom API endpoint for LLM calls
            api_key (str): API key for authentication with LLM service
        """
        self.verbose = verbose
        self.llm_api = LLMApi(verbose=verbose, api_endpoint=api_endpoint, api_key=api_key)
        self.prompt_refiner = PromptRefiner(verbose=verbose)
        
    def analyze_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Analyze all Python files in a directory and return file contents.
        
        Args:
            directory_path (str): Path to the directory containing Python files
            
        Returns:
            Dict[str, Any]: Dictionary containing analysis results for each file
        """
        if self.verbose:
            print(f"Analyzing directory: {directory_path}")
            
        # Get all Python files in directory
        python_files = FileHelper.directory_tree(directory_path, sort=True, file_extensions=['.py'])
        python_files = [f for f in python_files if not '__init__.py' in f]
        
        return self.analyze_files(python_files)
    
    def analyze_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Analyze specific Python files and return file contents.
        
        Args:
            file_paths (List[str]): List of paths to Python files
            
        Returns:
            Dict[str, Any]: Dictionary containing analysis results for each file
        """
        if self.verbose:
            print(f"Analyzing {len(file_paths)} files")
            
        analysis_results = {}
        
        for file_path in file_paths:
            try:
                # Read full file content instead of structured definitions
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                
                # Extract the raw AST data for more detailed analysis if needed
                classes, functions = PythonAnalyzer._get_class_and_function_definitions(file_path)
                
                analysis_results[file_path] = {
                    'filepath': file_path,
                    'file_content': file_content,
                    'classes': classes,
                    'functions': functions
                }
                
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
                analysis_results[file_path] = {
                    'filepath': file_path,
                    'error': str(e),
                    'file_content': '',
                    'classes': [],
                    'functions': []
                }
        
        return analysis_results
    
    def generate_review(self, code_analysis: Dict[str, Any], review_type: str = CODE_REVIEW_TYPE_ALL,
                        model: str = None, temperature: float = 0.7, max_tokens: int = 30000,
                        output_dir: str = None) -> Dict[str, Any]:
        """
        Generate a code review using LLM based on the analyzed code and specified review type.
        
        Args:
            code_analysis (Dict[str, Any]): Analysis results from analyze_directory or analyze_files
            review_type (str): Type of review to generate ("style", "security", "performance", "quality", "all")
            model (str): LLM model name to use for generation
            temperature (float): Sampling temperature for responses
            max_tokens (int): Maximum number of tokens for the review
            output_dir (str): Directory where markdown files will be saved immediately (optional)
            
        Returns:
            Dict[str, Any]: Dictionary containing the generated reviews
        """
        if self.verbose:
            print(f"Generating {review_type} review")
        
        # file listing markdown - if more than one file is reviewed - to provide more context
        all_file_paths = code_analysis.keys()
        file_list_markdown = ""
        if len(all_file_paths) > 1:
            file_list_markdown = "## Directory listing (as context for the code to review)"
            for file_path in all_file_paths:
                file_list_markdown = f"{file_list_markdown}\n- {file_path}"
        
        # If review_type is "all", we'll generate all types
        if review_type == CODE_REVIEW_TYPE_ALL:
            review_types = self.REVIEW_TYPES
        else:
            review_types = [review_type]
            
        reviews = {}
        
        for file_path, analysis in code_analysis.items():
            if self.verbose:
                print(f"Processing {file_path}")
                
            # Get the appropriate prompt template
            file_reviews = {}
            
            for review_type in review_types:
                try:
                    # Read the prompt template
                    with open(self.PROMPT_TEMPLATES[review_type], 'r') as f:
                        prompt_template = f.read()
                    
                    # Create a structured prompt that includes the full code content
                    prompt = (
                        f"{prompt_template}\n\n"
                        f"{file_list_markdown}\n\n"
                        f"## Code to Review\n"
                        f"Filepath: {file_path}\n"
                        "```\n"
                        f"{analysis['file_content']}\n"
                        "```\n\n"
                        "Please analyze this code and provide specific feedback based on the review criteria above."
                    )
                    
                    # Send to LLM for review generation
                    if model:
                        response = self.llm_api.send(prompt, model=model, temperature=temperature, max_tokens=max_tokens)
                    else:
                        response = self.llm_api.send(prompt, temperature=temperature, max_tokens=max_tokens)
                        
                    response = self.prompt_refiner.clean_response(response)
                    
                    file_reviews[review_type] = {
                        'review_type': review_type,
                        'file_path': file_path,
                        'prompt_template_used': self.PROMPT_TEMPLATES[review_type],
                        'generated_review': response
                    }
                    
                except Exception as e:
                    print(f"Error generating {review_type} review for {file_path}: {e}")
                    file_reviews[review_type] = {
                        'review_type': review_type,
                        'file_path': file_path,
                        'error': str(e),
                        'generated_review': None
                    }
            
            reviews[file_path] = file_reviews
            
            # If output_dir is specified, write the review immediately
            # (this prevents duplicate writes when both immediate and batch saving are used)
            if output_dir:
                try:
                    self._save_single_review(file_path, file_reviews, output_dir)
                except Exception as e:
                    print(f"Warning: Failed to save review for {file_path} immediately: {e}")
            
        return reviews

    def _save_single_review(self, file_path: str, file_reviews: Dict[str, Any], output_dir: str) -> str:
        """
        Save a single code review to markdown file immediately.
        
        Args:
            file_path (str): Path to the original Python file
            file_reviews (Dict[str, Any]): Review results for this file
            output_dir (str): Directory where markdown files will be saved
            
        Returns:
            str: Path to created markdown file
        """
        if self.verbose:
            print(f"Saving review for {file_path} to directory: {output_dir}")
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename based on original file path
        base_name = os.path.basename(file_path)
        name_without_ext = os.path.splitext(base_name)[0]
        output_file = os.path.join(output_dir, f"{name_without_ext}_review.md")
        
        # Create markdown content
        md_content = f"# Code Review for {base_name}\n\n"
        

        # Add individual reviews
        for review_type, review_data in file_reviews.items():
            md_content += f"\n## {review_type.capitalize()} Review\n\n"
            if 'generated_review' in review_data and review_data['generated_review']:
                md_content += review_data['generated_review']
            elif 'error' in review_data:
                md_content += f"Error during review generation: {review_data['error']}\n"
        
        # Write to file
        FileHelper.write_to_file(output_file, md_content, verbose=self.verbose)
        
        return output_file


# For backward compatibility and direct usage
def run_code_review(directory_path: str = None, file_paths: List[str] = None,
                   output_dir: str = "reviews", review_type: str = CODE_REVIEW_TYPE_ALL,
                   model: str = None, api_endpoint: str = None, 
                   api_key: str = None, max_tokens: int = 30000, verbose: bool = False) -> Dict[str, Any]:
    """
    Convenience function to run a code review workflow.
    
    Args:
        directory_path (str): Path to directory containing Python files
        file_paths (List[str]): List of specific Python file paths  
        output_dir (str): Directory for output markdown files
        review_type (str): Type of review ("style", "security", "performance", "quality", "all")
        model (str): LLM model name to use
        api_endpoint (str): Custom API endpoint
        api_key (str): API key for authentication
        verbose (bool): Enable verbose output
        max_tokens (int): Maximum number of tokens for the review
        
    Returns:
        Dict[str, Any]: Review results
    """
    workflow = CodeReviewWorkflow(verbose=verbose, api_endpoint=api_endpoint, api_key=api_key)
    
    # Analyze code based on input parameters
    if directory_path:
        analysis_results = workflow.analyze_directory(directory_path)
    elif file_paths:
        analysis_results = workflow.analyze_files(file_paths)
    else:
        raise ValueError("Either directory_path or file_paths must be specified")
        
    # Generate reviews - with immediate writing capability
    reviews = workflow.generate_review(analysis_results, review_type=review_type, model=model, max_tokens=max_tokens, output_dir=output_dir)
    
    return reviews