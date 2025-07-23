# File Helper Script

# This script provides a `FileHelper` class with static methods for common
# file system operations. It includes functionalities for cleaning filenames,
# listing, reading, writing, and creating files, as well as combining
# content from multiple files or directories. This utility centralizes
# file management operations for the LLM tools.

# Usage Example:
# from src.llm_tools.file_helper import FileHelper
# files = FileHelper.list_files_in_directory('/path/to/dir')
# content = FileHelper.read_file('file.txt')

import os
import json
from typing import List
from .colors import Colors
from datetime import datetime

class FileHelper:
    """
    A utility class providing static methods for various file system operations.
    Encapsulates common tasks like file reading, writing, directory listing,
    and filename sanitization.

    This class contains the following static methods:
    - clean_name()
    - list_files_in_directory()
    - read_file()
    - read_multiple_files()
    - read_multiple_files_from_directories()
    - write_to_file()
    - create_new_file()
    - generate_postfixed_sub_directory_name()
    - combine_files()
    - combine_files_in_directories()

    Note: All methods are static and do not require class instantiation.
    """
    
    @staticmethod
    def clean_name(name: str) -> str:
        """
        Cleans up a given string to be suitable for use as a filename or path component.
        Replaces common special characters that are problematic in file names with
        underscores or hyphens, and removes others.

        Args:
            name (str): The original name string that needs cleaning.

        Returns:
            str: The cleaned-up string, safe for file system use.
        """
        return name.replace('/', '_').replace(':', '-').replace('*', '-').replace('?', '').replace('"', '')

    @staticmethod
    def list_files_in_directory(directory_path: str, verbose: bool = False) -> List[str]:
        """
        Lists all files directly within a specified directory (non-recursive).

        Args:
            directory_path (str): The path to the directory to scan.
            verbose (bool): If True, enables verbose output (currently not used in this method).

        Returns:
            List[str]: A list of full file paths found in the directory.
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
            file_path (str): The path to the file to be read.
            verbose (bool): If True, prints a message indicating the file being loaded.

        Returns:
            str: The stripped content of the file.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            IOError: If an error occurs during file reading.
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
        Reads and returns the content of multiple files.

        Args:
            file_paths (List[str]): A list of paths to the files to be read.
            verbose (bool): If True, enables verbose output for each file read.

        Returns:
            List[str]: A list containing the stripped content of each file.

        Raises:
            FileNotFoundError: If any of the specified files do not exist.
            IOError: If an error occurs during reading any of the files.
        """
        contents = []
        for file_path in file_paths:
            contents.append(FileHelper.read_file(file_path, verbose=verbose))
        return contents
    
    @staticmethod
    def read_multiple_files_from_directories(directory_paths: List[str], verbose: bool = False) -> List[str]:
        """
        Reads and returns the content of all files found within multiple specified directories.

        Args:
            directory_paths (List[str]): A list of paths to directories from which to read files.
            verbose (bool): If True, enables verbose output during file listing and reading.
            
        Returns:
            List[str]: A list containing the stripped content of all files found.
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
        Writes the given content to a specified file. Creates parent directories if they don't exist.

        Args:
            file_path (str): The path to the file where content will be written.
            content (str): The string content to write to the file.
            verbose (bool): If True, prints a success message upon successful writing.

        Raises:
            IOError: If an error occurs during file writing.
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
    def create_new_file(file_path: str, verbose: bool = False) -> None:
        """
        Creates a new empty file at the specified path. Creates parent directories if they don't exist.

        Args:
            file_path (str): The path to the file to be created.
            verbose (bool): If True, prints a success message upon successful file creation.

        Raises:
            IOError: If an error occurs during file creation.
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
        Generates a new subdirectory name by appending the current date and time
        (YYYY-MM-DD_HH-MM format) to a base directory name.

        Args:
            base_directory (str): The base directory path.

        Returns:
            str: The new directory path with a datetime postfix.
        """
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M")
        return f"{base_directory}/{formatted_datetime}"
    
    @staticmethod
    def combine_files(file_paths: List[str], verbose: bool = False) -> str:
        """
        Combines the content of multiple files into a single string,
        separated by a '---' delimiter.

        Args:
            file_paths (List[str]): A list of paths to the files to combine.
            verbose (bool): If True, enables verbose output during file reading.

        Returns:
            str: A single string containing the combined content of all files.

        Raises:
            Exception: If no file paths are provided.
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
        Combines the content of all files found within multiple specified directories
        into a single string, separated by a '---' delimiter.

        Args:
            directory_paths (List[str]): A list of paths to directories containing files to combine.
            verbose (bool): If True, enables verbose output during file listing and reading.

        Returns:
            str: A single string containing the combined content of all files from the directories.

        Raises:
            Exception: If no directory paths are provided.
        """
        if directory_paths is None:
            raise Exception("No directory_paths provided")
        
        file_list=[]
        for directory_path in directory_paths:
            file_list += FileHelper.list_files_in_directory(directory_path, verbose=verbose)
        return FileHelper.combine_files(file_list, verbose=verbose)