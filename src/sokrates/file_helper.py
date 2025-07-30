# File Helper Script

# This script provides a `FileHelper` class with static methods for common
# file system operations. It includes functionalities for cleaning filenames,
# listing, reading, writing, and creating files, as well as combining
# content from multiple files or directories. This utility centralizes
# file management operations for the LLM tools.

# Usage Example:
# from src.sokrates.file_helper import FileHelper
# files = FileHelper.list_files_in_directory('/path/to/dir')
# content = FileHelper.read_file('file.txt')

import os
import json
from typing import List
from .colors import Colors
from datetime import datetime
import shutil
from pathlib import Path

class FileHelper:
    """
    A utility class providing static methods for various file system operations.

    This class contains the following static methods:
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

    Main Responsibilities:
        - File path sanitization and manipulation
        - Reading/writing file content with error handling
        - Directory operations and file combination utilities

    Note: All methods are static and do not require class instantiation.
    """
    
    @staticmethod
    def clean_name(name: str) -> str:
        """
        Sanitizes a string for use as a filename or path component.

        Replaces problematic characters:
        - '/' → '_'
        - ':' → '-'
        - '*' → '-'
        - '?' → '' (removed)
        - '"' → '' (removed)

        Args:
            name (str): Input string to clean

        Returns:
            str: Safe filename string
        """
        return name.replace('/', '_').replace(':', '-').replace('*', '-').replace('?', '').replace('"', '')

    @staticmethod
    def list_files_in_directory(directory_path: str, verbose: bool = False) -> List[str]:
        """
        Lists all files directly within a specified directory (non-recursive).

        Args:
            directory_path (str): Directory path to scan
            verbose (bool, optional): Verbose output flag

        Returns:
            List[str]: List of full file paths found
        """
        file_paths = []
        for file_path in os.scandir(directory_path):
            if os.path.isfile(file_path.path):
                file_paths.append(file_path.path)
        return file_paths
    
    @staticmethod
    def read_json_file(file_path: str, verbose: bool = False) -> dict:
        if verbose:
            print(f"{Colors.CYAN}Loading json file from {file_path} ...{Colors.RESET}")
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def read_file(file_path: str, verbose: bool = False) -> str:
        """
        Reads and returns the entire content of a specified file.

        Args:
            file_path (str): Path to the file to read
            verbose (bool, optional): If True, prints loading messages

        Returns:
            str: Stripped file content

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: For other file reading errors
        """
        try:
            if verbose:
                print(f"{Colors.CYAN}Loading file from {file_path} ...{Colors.RESET}")
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except IOError as e:
            raise IOError(f"Error reading file {file_path}: {e}")
    
    @staticmethod
    def read_multiple_files(file_paths: List[str], verbose: bool = False) -> List[str]:
        """
        Reads content from multiple files.

        Args:
            file_paths (List[str]): List of file paths to read
            verbose (bool, optional): Enable verbose output

        Returns:
            List[str]: List of stripped file contents

        Raises:
            FileNotFoundError: If any file doesn't exist
            IOError: For reading errors
        """
        contents = []
        for file_path in file_paths:
            contents.append(FileHelper.read_file(file_path, verbose=verbose))
        return contents
    
    @staticmethod
    def read_multiple_files_from_directories(directory_paths: List[str], verbose: bool = False) -> List[str]:
        """
        Reads all files from multiple directories.

        Args:
            directory_paths (List[str]): List of directory paths to scan
            verbose (bool, optional): Enable verbose output

        Returns:
            List[str]: Combined content of all found files
        """
        contents=[]
        for directory_path in directory_paths:
            file_list = FileHelper.list_files_in_directory(directory_path, verbose=verbose)
            file_contents = FileHelper.read_multiple_files(file_list, verbose=verbose)
            for fc in file_contents:
                contents.append(fc)
        return contents

    @staticmethod
    def write_to_file(file_path: str, content: str, verbose: bool = False) -> None:
        """
        Writes content to a file, creating parent directories as needed.

        Args:
            file_path (str): Destination file path
            content (str): Content to write
            verbose (bool, optional): If True, prints success message

        Raises:
            IOError: For directory creation or writing errors
        """
        try:
            dirname = os.path.dirname(file_path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            if verbose:
                print(f"{Colors.GREEN}Content successfully written to {file_path}{Colors.RESET}")
        except IOError as e:
            raise IOError(f"Error writing to file {file_path}: {e}")

    @staticmethod
    def copy_file(source_filepath, target_filepath, verbose:bool = False):
        try:
            shutil.copy2(source_filepath, target_filepath, follow_symlinks=True)
            if verbose:
                print(f"{Colors.GREEN}File copied successfully from {source_filepath} to {target_filepath}{Colors.RESET}")
        
        except FileNotFoundError:
            print(f"{Colors.RED}Error: Source file not found at {source_filepath}{Colors.RESET}")
            raise 
        except PermissionError:
            print(f"{Colors.RED}Error: Permission denied.{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}An error occurred: {e}{Colors.RESET}")
            raise e

    @staticmethod
    def create_new_file(file_path: str, verbose: bool = False) -> None:
        """
        Creates empty file with parent directories.

        Args:
            file_path (str): Path to create
            verbose (bool, optional): Print success message

        Raises:
            IOError: For creation errors
        """
        try:
            dirname = os.path.dirname(file_path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write("")
            if verbose:
                print(f"{Colors.GREEN}File successfully created at {file_path}{Colors.RESET}")
        except IOError as e:
            raise IOError(f"Error creating file {file_path}: {e}")

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
    def generate_postfixed_file_path(file_path: str) -> str:
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
    def combine_files(file_paths: List[str], verbose: bool = False) -> str:
        """
        Combines multiple files into single string with '---' separators.

        Args:
            file_paths (List[str]): List of file paths to combine
            verbose (bool, optional): Enable verbose output

        Returns:
            str: Combined content with separators

        Raises:
            Exception: If no files provided
        """
        if file_paths is None:
            raise Exception("No files provided")
        
        combined_content = ""
        for file_path in file_paths:
            combined_content = f"{combined_content}\n---\n{FileHelper.read_file(file_path, verbose=verbose)}"
        return combined_content
    
    @staticmethod
    def combine_files_in_directories(directory_paths: List[str], verbose: bool = False) -> str:
        """
        Combines all files from directories into single string with '---' separators.

        Args:
            directory_paths (List[str]): List of directories to scan
            verbose (bool, optional): Enable verbose output

        Returns:
            str: Combined content from all directories

        Raises:
            Exception: If no directories provided
        """
        if directory_paths is None:
            raise Exception("No directory_paths provided")
        
        file_list=[]
        for directory_path in directory_paths:
            file_list += FileHelper.list_files_in_directory(directory_path, verbose=verbose)
        return FileHelper.combine_files(file_list, verbose=verbose)