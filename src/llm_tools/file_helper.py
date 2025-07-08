import os
from typing import List
from .colors import Colors
from datetime import datetime

"""
A class for managing file operations.
"""
class FileHelper:
    
    @staticmethod
    def clean_name(name: str) -> str:
        """Provide a cleaned-up name as input to file names.

        Replaces all special characters with underscores, hyphens, asterisks, question marks, and double quotes.

        Args:
            name (str): The original name string.

        Returns:
            str: Cleaned-up name.
        """
        return name.replace('/', '_').replace(':', '-').replace('*', '-').replace('?', '').replace('"', '')

    @staticmethod
    def list_files_in_directory(directory_path: str, verbose: bool = False) -> list[str]:
        """List all files in a directory.

        Args:
            directory_path (str): Path to the directory.

        Returns:
            list[str]: List of file names in the directory.
        """
        file_paths = []
        for file_path in os.scandir(directory_path):
            if os.path.isfile(file_path.path):
                file_paths.append(file_path.path)
        return file_paths

    @staticmethod
    def read_file(file_path: str, verbose: bool = False) -> str:
        """Load and return the content of a prompt file.

        Args:
            file_path (str): Path to the prompt file.

        Returns:
            str: Content of the prompt file.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            IOError: If there's an error reading the file.
        """
        try:
            if verbose:
                print(f"{Colors.CYAN}Loading file from {file_path} ...{Colors.RESET}")
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except IOError as e:
            raise IOError(f"Error reading file: {e}")

    @staticmethod
    def write_to_file(file_path: str, content: str, verbose: bool = False) -> None:
        """Save content to a file.

        Args:
            content (str): Content to save.
            file_path (str): Output filename.

        Raises:
            IOError: If there's an error writing to the file.
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
        """Create a new empty file.

        Args:
            file_path (str): Path to the file to create.
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
        current_datetime = datetime.now()
        # Format the current date and time
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M")
        return f"{base_directory}/{formatted_datetime}"
    
    @staticmethod
    def combine_files(file_paths: List[str], verbose: bool = False):
        if file_paths is None:
            raise Exception("No files provided")
        
        combined_content = ""
        for file_path in file_paths:
            combined_content = f"{combined_content}\n---\n{FileHelper.read_file(file_path, verbose=verbose)}"
        return combined_content

                