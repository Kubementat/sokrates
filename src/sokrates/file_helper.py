# File Helper Script

# This script provides a `FileHelper` class with static methods for common
# file system operations. It includes functionalities for cleaning filenames,
# listing, reading, writing, and creating files, as well as combining
# content from multiple files or directories. This utility centralizes
# file management operations for the LLM tools.

# Main Purpose:
# - Provides a centralized utility for common file system operations
# - Includes file management functions for reading, writing, listing, and creating files
# - Supports combining content from multiple files or directories
# - Includes filename sanitization and timestamped directory/file naming

# Parameters:
# - All methods are static and don't require class instantiation
# - Some methods accept lists of file paths for batch operations

# Usage Example:
# from src.sokrates.file_helper import FileHelper
# files = FileHelper.list_files_in_directory('/path/to/dir')
# content = FileHelper.read_file('file.txt')

import os
import json
from typing import List
from datetime import datetime
import shutil
from pathlib import Path
import re
import logging

class FileHelper:
    """
    A utility class providing static methods for various file system operations.

    Main Purpose:
        - Centralizes common file system operations for LLM tools
        - Provides file management functions for reading, writing, listing, and creating files
        - Supports combining content from multiple files or directories
        - Includes filename sanitization and timestamped directory/file naming

    Initialization Parameters:
        - None (all methods are static and don't require class instantiation)

    Functions:
        - clean_name(): Sanitize filenames by removing problematic characters
        - list_files_in_directory(): List files in a directory (non-recursive)
        - read_file(): Read content from a single file
        - read_multiple_files(): Read content from multiple files
        - read_multiple_files_from_directories(): Read all files from directories
        - write_to_file(): Write content to a file with directory creation
        - create_new_file(): Create empty files with directory creation
        - generate_postfixed_sub_directory_name(): Generate timestamped directory names
        - combine_files(): Combine multiple files into single string
        - combine_files_in_directories(): Combine all files from directories
    """

    _log = logging.getLogger(__name__) 
    
    @staticmethod
    def clean_name(name: str) -> str:
        """
        Sanitizes a string for use as a filename or path component.

        Main Functionality:
            - Replaces problematic characters with safe alternatives
            - Removes question marks and quotes

        Args:
            name (str): Input string to clean

        Returns:
            str: Safe filename string with problematic characters replaced

        Side Effects:
            - None (pure function)
        """
        result = name.replace('/', '_').replace(':', '-').replace('*', '-').replace('?', '').replace('"', '').replace(' ', '-')
        if len(result) < 1 or bool(re.match(r'^[_-]*$', result)):
            error = f"The provided name: {name} can't be resolved to a clean name."
            FileHelper._log.error(error)
            raise ValueError(error)
        return result

    @staticmethod
    def list_files_in_directory(directory_path: str | Path) -> List[str]:
        """
        Lists all files directly within a specified directory (non-recursive).

        Main Functionality:
            - Scans a directory and returns all files (not subdirectories)
            - Uses os.scandir for efficient file system access

        Args:
            directory_path (str): Directory path to scan

        Returns:
            List[str]: List of full file paths found in the directory

        Side Effects:
            - None (pure function)
        """
        dir_path = Path(directory_path)
        return [str(p.resolve()) for p in dir_path.iterdir() if p.is_file()]
    
    @staticmethod
    def read_json_file(file_path: str | Path) -> dict:
        """
        Reads and parses a JSON file.

        Main Functionality:
            - Opens and reads a JSON file
            - Parses the JSON content into a Python dictionary

        Args:
            file_path (str | Path): Path to the JSON file to read

        Returns:
            dict: Parsed JSON content

        Side Effects:
            - None (pure function)
        """
        path_obj = Path(file_path)
        with open(path_obj, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def read_file(file_path: str | Path) -> str:
        """
        Reads and returns the entire content of a specified file.

        Main Functionality:
            - Opens a file and reads its entire content
            - Strips whitespace from the beginning and end of the content
            - Handles file reading errors with appropriate exceptions

        Args:
            file_path (str): Path to the file to read

        Returns:
            str: Stripped file content

        Side Effects:
            - None (pure function)
        """
        try:
            return Path(file_path).read_text(encoding='utf-8', errors='replace')
        except FileNotFoundError:
            error = f"File not found: {file_path}"
            FileHelper._log.error(error)
            raise
        except IOError as e:
            error = f"Error reading file {file_path}: {e}"
            FileHelper._log.error(error)
            raise
    
    @staticmethod
    def read_multiple_files(file_paths: List[str] | List[Path]) -> List[str]:
        """
        Reads content from multiple files.

        Main Functionality:
            - Reads multiple files specified by their paths
            - Returns a list of stripped content from each file
            - Handles file reading errors with appropriate exceptions

        Args:
            file_paths (List[str]): List of file paths to read

        Returns:
            List[str]: List of stripped file contents

        Side Effects:
            - None (pure function)
        """
        contents = []
        for file_path in file_paths:
            contents.append(FileHelper.read_file(file_path))
        return contents
    
    @staticmethod
    def read_multiple_files_from_directories(directory_paths: List[str]| List[Path]) -> List[str]:
        """
        Reads all files from multiple directories.

        Main Functionality:
            - Scans multiple directories and reads all files within them
            - Combines content from all files into a single list
            - Uses the list_files_in_directory and read_multiple_files methods

        Args:
            directory_paths (List[str]): List of directory paths to scan

        Returns:
            List[str]: Combined content of all found files

        Side Effects:
            - None (pure function)
        """
        contents=[]
        for directory_path in directory_paths:
            file_list = FileHelper.list_files_in_directory(directory_path)
            file_contents = FileHelper.read_multiple_files(file_list)
            for fc in file_contents:
                contents.append(fc)
        return contents

    @staticmethod
    def write_to_file(file_path: str | Path, content: str) -> None:
        """
        Writes *content* to the file specified by *file_path*, creating any missing
        parent directories along the way.

        Parameters
        ----------
        file_path : str | pathlib.Path
            Destination path. Can be a plain string or a `Path` instance.
        content : str
            Text to write into the file.

        Raises
        ------
        IOError
            If an I/O error occurs while creating directories or writing the file.
        """
        try:
            # Ensure we have a native OS‑path string; this works for both str and Path.
            path = os.fspath(file_path)

            # Create parent directory(ies) if they don't exist.
            dirname = os.path.dirname(path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)

            # Write the content to the file
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except IOError as e:
            error_msg = f"Error writing to file {file_path!s}: {e}"
            FileHelper._log.error(error_msg)
            raise

    @staticmethod
    def copy_file(source_filepath: str | Path, target_filepath: str | Path):
        """
        Copies a file from source to target path.

        Main Functionality:
            - Uses shutil.copy2 to copy a file with metadata preservation
            - Creates parent directories as needed for the target path
            - Handles various error conditions with appropriate messages

        Args:
            source_filepath (str): Path to the source file to copy
            target_filepath (str): Destination path for the copied file

        Returns:
            None

        Side Effects:
            - Creates parent directories for target path if needed
            - Copies file content and metadata from source to destination

        Raises:
            FileNotFoundError: If the source file doesn't exist
            PermissionError: If there's no permission to read or write files
            Exception: For other unexpected errors during copying process

        Example:
            FileHelper.copy_file('/path/to/source.txt', '/path/to/target.txt')
        """
        shutil.copy2(str(source_filepath), str(target_filepath), follow_symlinks=True)

    @staticmethod
    def create_new_file(file_path: str) -> None:
        """
        Creates empty file with parent directories.

        Args:
            file_path (str): Path to create

        Raises:
            IOError: For creation errors
        """
        try:
            dirname = os.path.dirname(file_path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write("")
        except IOError as e:
            error = f"Error creating file {file_path}: {e}"
            FileHelper._log.error(error)
            raise

    @staticmethod
    def delete_file(file_path: str | Path) -> None:
        """
        Deletes a file at the given path.

        Args:
            file_path (str): Path to create

        """
        Path(file_path).unlink(missing_ok=True)

    @staticmethod
    def generate_postfixed_sub_directory_name(base_directory: str) -> str:
        """
        Generates timestamped subdirectory name.

        Args:
            base_directory (str): Base directory path

        Returns:
            str: Directory path with YYYY-MM-DD_HH-MM postfix
        """
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M")
        return f"{base_directory}/{formatted_datetime}"
    
    @staticmethod
    def generate_postfixed_file_path(file_path: str | Path) -> str:
        """
        Generates timestamped file path from a given file path.

        Args:
            file_path (str): Base file path
        Returns:
            str: file path with YYYY-MM-DD_HH-MM.EXTENSION postfix
        """
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M")
        path = Path(file_path)
        full_path_without_extension = path.with_suffix("")
        file_extension = path.suffix
        return str(Path(f"{full_path_without_extension}_{formatted_datetime}.{file_extension}"))
    
    @staticmethod
    def combine_files(file_paths: List[str] | List[Path]) -> str:
        """
        Combines multiple files into single string with '---' separators.

        Args:
            file_paths (List[str]): List of file paths to combine

        Returns:
            str: Combined content with separators

        Raises:
            Exception: If no files provided
        """
        if file_paths is None:
            raise Exception("No files provided")
        
        combined_content = ""
        for file_path in file_paths:
            combined_content = f"{combined_content}\n---\n{FileHelper.read_file(file_path)}"
        return combined_content
    
    @staticmethod
    def combine_files_in_directories(directory_paths: List[str]) -> str:
        """
        Combines all files from directories into single string with '---' separators.

        Args:
            directory_paths (List[str]): List of directories to scan

        Returns:
            str: Combined content from all directories

        Raises:
            ValueError: If no directories provided
        """
        if directory_paths is None:
            raise ValueError("No directory_paths provided")
        
        file_list=[]
        for directory_path in directory_paths:
            file_list += FileHelper.list_files_in_directory(directory_path)
        return FileHelper.combine_files(file_list)

    @staticmethod
    def directory_tree(directory, exclude_patterns=None, sort=False, file_extensions=None):
        """
        Generate a tree structure of all files in the given directory.
        
        Args:
            directory (str): Path to the directory to scan
            exclude_patterns (list): List of compiled regex patterns to exclude
            sort (bool): Whether to sort the output
            file_extensions (list): List of file extensions to include (e.g., ['.py', '.js'])
        
        Returns:
            list: List of full file paths
        """
        if exclude_patterns is None:
            exclude_patterns = [
                re.compile(r'\.venv'),
                re.compile(r'__pycache__'),
                re.compile(r'\.pytest_cache'),
                re.compile(r'.*\.egg-info.*')
            ]
        
        file_paths = []
        
        try:
            # Walk through directory tree
            for root, dirs, files in os.walk(directory):
                # Get full paths of directories to exclude (before modification)
                dirs_to_exclude = []
                
                for i, dir_name in enumerate(dirs):
                    for pattern in exclude_patterns:
                        if pattern.search(dir_name) or pattern.match(dir_name):
                            dirs_to_exclude.append(i)
                
                # Filter out excluded directories
                filtered_dirs = [d for i, d in enumerate(dirs) if i not in dirs_to_exclude]
                
                # Update dirs to filtered list (this affects the actual walk)
                dirs[:] = [d for i, d in enumerate(dirs) if i not in dirs_to_exclude]
                
                # Process files within current directory
                for file in files:
                    full_file_path = os.path.join(root, file)
                    abs_path = os.path.abspath(full_file_path)
                    
                    # Check if this file should be excluded based on patterns
                    is_excluded = False
                    
                    for pattern in exclude_patterns:
                        try:
                            # Check if this pattern matches any part of the path
                            file_path_str = str(full_file_path)
                            
                            # Check if pattern matches the filename or full path components
                            if pattern.search(file_path_str):
                                is_excluded = True
                                break
                            
                            # Also check if pattern matches the file basename directly
                            filename = os.path.basename(full_file_path)
                            if pattern.match(filename):
                                is_excluded = True
                                break
                            
                        except Exception:
                            continue
                    
                    # If not excluded, check if we should include based on extensions
                    if not is_excluded:
                        # If no specific file extensions requested, include all files
                        if file_extensions is None:
                            file_paths.append(abs_path)
                        else:
                            # Check if the file has one of the allowed extensions
                            file_ext = os.path.splitext(full_file_path)[1].lower()
                            if file_ext in [ext.lower() for ext in file_extensions]:
                                file_paths.append(abs_path)
                
        except PermissionError as e:
            FileHelper._log.error(f"Permission denied accessing some directories: {e}")
        except Exception as e:
            FileHelper._log.error(f"Error processing directory {directory}: {e}")
        
        # Sort if requested
        if sort:
            file_paths.sort()
        
        return file_paths

    @staticmethod
    def create_and_return_task_execution_directory(output_directory=None) -> str:
        """
        Creates and returns the target directory for task results.

        Args:
            output_directory (Path, optional): Path to custom output directory.
                If provided, creates this directory. If None, uses default path in $HOME/.sokrates/tasks/results/YYYY-MM-DD_HH-mm .

        Returns:
            Path: Path object pointing to the created directory

        Raises:
            FileExistsError: If the specified output directory already exists
        """
        if output_directory:
            Path(output_directory).mkdir(parents=True, exist_ok=True)
            return output_directory
        
        # use default if not specified
        now = datetime.now()
        home_dir = Path.home()
        
        # Format the directory name as 'YYYY-MM-DD_HH-MM'
        directory_name = now.strftime("%Y-%m-%d_%H-%M")
        
        default_task_result_parent_dir = home_dir / ".sokrates" / "tasks" / "results"
        target_dir = Path(default_task_result_parent_dir) / directory_name
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        
        return str(target_dir)