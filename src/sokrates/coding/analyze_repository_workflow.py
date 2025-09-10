from pathlib import Path
from typing import Dict, List, Any, Optional
import re
import logging

from sokrates.file_helper import FileHelper
from sokrates.llm_api import LLMApi
from sokrates.prompt_refiner import PromptRefiner
from sokrates.constants import Constants
from sokrates.prompt_constructor import PromptConstructor

class AnalyzeRepositoryWorkflow:
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_PROMPT_TEMPLATE_NAME = "analyze_repository.md"
    DEFAULT_MAX_TOKENS = 20000
    DEFAULT_EXCLUDE_PATTERNS = [
        re.compile(r'\.venv'),
        re.compile(r'__pycache__'),
        re.compile(r'\.pytest_cache'),
        re.compile(r'.*\.egg-info.*'),
        re.compile(r'.*__cache__.*'),
        re.compile(r'.*site-packages.*')
    ]

    def __init__(self, api_endpoint: str, api_key: str) -> None:
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.llm_api = LLMApi(api_endpoint=api_endpoint, api_key=api_key)

    def analyze_repository(self, source_directory: str, model: str, temperature: float = DEFAULT_TEMPERATURE, max_tokens: int = DEFAULT_MAX_TOKENS, exclude_patterns: Optional[List[re.Pattern]] = None) -> str:
        self.logger.info(f"Started analysis for directory: {source_directory} ...")
        
        try:
            # Use provided exclude patterns or default ones
            if exclude_patterns is None:
                patterns_to_use = self.DEFAULT_EXCLUDE_PATTERNS
            else:
                patterns_to_use = exclude_patterns
                
            file_paths = FileHelper.directory_tree(directory=source_directory, exclude_patterns=patterns_to_use)
            self.logger.debug(f"Found {len(file_paths)} files in directory: {source_directory}")

            # Search for readme files in file_paths
            readme_files = self._filter_readme_filepaths(file_paths=file_paths)
            self.logger.debug(f"Found {len(readme_files)} README files")

            # read readme contents
            readme_file_content = self._construct_readme_file_content(readme_files)
            
            # Search for markdown files in file_paths
            markdown_files = self._filter_non_readme_markdown_file_paths(file_paths=file_paths)
            self.logger.debug(f"Found {len(markdown_files)} non-README markdown files")

            # construct prompt using template
            prompt = self._construct_prompt_from_template(data={
                "ALL_FILE_PATHS": file_paths,
                "README_FILE_PATHS": readme_files,
                "MARKDOWN_FILE_PATHS": markdown_files,
                "README_FILES_CONTENT": readme_file_content
            })
            
            # send prompt and cleanup answer
            self.logger.debug("Sending prompt to LLM API")
            answer = self.llm_api.send(prompt=prompt, model=model, temperature=temperature, max_tokens=max_tokens)
            cleaned_answer = PromptRefiner().clean_response(answer)

            self.logger.info(f"Finished analysis for directory: {source_directory}")
            return cleaned_answer
            
        except Exception as e:
            self.logger.error(f"Error during repository analysis: {str(e)}")
            raise
        
    
    def _filter_readme_filepaths(self, file_paths: List[str]) -> List[str]:
        """Filter file paths to only include README files using Path-based approach."""
        readme_files = []
        for path in file_paths:
            try:
                p = Path(path)
                # Match files that contain "README" (case insensitive) and end with .md
                if p.suffix == '.md' and 'README' in p.name.upper():
                    readme_files.append(str(p))
            except Exception as e:
                self.logger.warning(f"Error processing path {path}: {str(e)}")
                continue
        return readme_files
    
    def _filter_non_readme_markdown_file_paths(self, file_paths: List[str]) -> List[str]:
        """Filter file paths to only include non-README markdown files using Path-based approach."""
        markdown_files = []
        for path in file_paths:
            try:
                p = Path(path)
                # Match files that end with .md but do NOT contain "README" (case insensitive)
                if p.suffix == '.md' and 'README' not in p.name.upper():
                    markdown_files.append(str(p))
            except Exception as e:
                self.logger.warning(f"Error processing path {path}: {str(e)}")
                continue
        return markdown_files
    
    def _construct_prompt_from_template(self, data: Dict[str, Any], template_name: str = DEFAULT_PROMPT_TEMPLATE_NAME) -> str:
        try:
            template_full_path = (Constants.DEFAULT_CODING_PROMPTS_DIRECTORY / template_name).resolve()
            
            all_file_paths = "\n".join(f"- {path}" for path in data.get('ALL_FILE_PATHS', []))
            readme_file_paths = "\n".join(f"- {path}" for path in data.get('README_FILE_PATHS', []))
            markdown_file_paths = "\n".join(f"- {path}" for path in data.get('MARKDOWN_FILE_PATHS', []))
            readme_files_content = data.get('README_FILES_CONTENT')
            
            replacement_data = {
                "ALL_FILE_PATHS": all_file_paths,
                "README_FILE_PATHS": readme_file_paths,
                "MARKDOWN_FILE_PATHS": markdown_file_paths,
                "README_FILES_CONTENT": readme_files_content
            }
            
            prompt = PromptConstructor.construct_prompt_from_template_file(template_file_path=template_full_path, data=replacement_data)
            self.logger.debug("Prompt constructed successfully from template")
            return prompt
            
        except Exception as e:
            self.logger.error(f"Error constructing prompt from template: {str(e)}")
            raise
        
    def _construct_readme_file_content(self, readme_files: List[str]) -> str:
        """Construct README file content with proper error handling."""
        if not readme_files:
            return ""
        
        try:
            readme_files_raw = FileHelper.read_multiple_files(readme_files)
            
            # Simplified loop construction
            readme_content_parts = []
            for i, (file_path, content) in enumerate(zip(readme_files, readme_files_raw)):
                readme_content_parts.append(f"<file path='{file_path}'>{content}</file>\n\n")
            
            return "".join(readme_content_parts)
        except Exception as e:
            self.logger.error(f"Error constructing README file content: {str(e)}")
            raise