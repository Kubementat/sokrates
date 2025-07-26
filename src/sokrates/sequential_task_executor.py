#!/usr/bin/env python3
"""
Sequential Task Executor Module

This module provides functionality to execute tasks defined in a JSON file sequentially.
It leverages existing refinement workflows and LLM interaction capabilities.

Classes:
    SequentialTaskExecutor: Main class for executing sequential tasks from JSON files.
"""

import os
from typing import List, Dict
from .refinement_workflow import RefinementWorkflow
from .file_helper import FileHelper
from .config import Config

class SequentialTaskExecutor:
    """
    Executes tasks defined in a JSON file sequentially.

    This class reads tasks from a JSON file (same format as BreakdownTask output),
    processes each task by analyzing concepts, generating prompts, refining them,
    and executing the tasks using LLM APIs. Results are saved to a specified directory.

    Main Responsibilities:
        - Load tasks from JSON files
        - Process tasks sequentially with error handling
        - Manage refinement workflows for prompt generation
        - Save execution results to output directory

    Attributes:
        api_endpoint (str): API endpoint for LLM service
        api_key (str): Authentication key for API access
        model (str): LLM model identifier
        output_dir (str): Directory path for saving results
        verbose (bool): Verbose output flag
        workflow (RefinementWorkflow): Workflow instance for prompt refinement

    Methods:
        execute_tasks_from_file(): Execute all tasks from a JSON file
        _process_single_task(): Process individual task with refinement and execution
    """

    def __init__(self, api_endpoint: str = Config.DEFAULT_API_ENDPOINT,
                 api_key: str = Config.DEFAULT_API_KEY,
                 model: str = Config.DEFAULT_MODEL,
                 output_dir: str = None,
                 verbose: bool = False):
        """
        Initializes the SequentialTaskExecutor with configuration and workflow setup.

        Args:
            api_endpoint (str): LLM API endpoint. Defaults to Config.DEFAULT_API_ENDPOINT.
            api_key (str): API key for authentication. Defaults to Config.DEFAULT_API_KEY.
            model (str): LLM model to use. Defaults to Config.DEFAULT_MODEL.
            output_dir (str, optional): Directory where task results will be saved.
                If None, defaults to "./task_results".
            verbose (bool, optional): If True, enables verbose output. Defaults to False.

        Side Effects:
            - Creates output directory if it doesn't exist
            - Initializes refinement workflow instance
        """
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.model = model
        self.output_dir = output_dir or "./task_results"
        self.verbose = verbose

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Initialize refinement workflow
        self.workflow = RefinementWorkflow(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key,
            model=self.model,
            verbose=self.verbose
        )

    def execute_tasks_from_file(self, task_file_path: str) -> Dict[str, any]:
        """
        Executes all tasks from a JSON file sequentially.

        Args:
            task_file_path (str): Path to the JSON file containing tasks

        Returns:
            dict: Summary of execution results with success/failure counts and details.
                Contains keys:
                - total_tasks: Total number of tasks processed
                - successful_tasks: Count of successfully completed tasks
                - failed_tasks: Count of failed tasks
                - details: List of individual task execution details

        Raises:
            ValueError: If task file cannot be loaded or parsed
            Exception: If any task processing fails (caught and counted as failure)

        Side Effects:
            - Modifies internal state with task execution results
            - Creates output files in the specified directory
        """
        if self.verbose:
            print(f"Loading tasks from {task_file_path}...")

        # Load tasks from JSON file
        try:
            tasks = FileHelper.read_json_file(task_file_path, verbose=self.verbose)
        except Exception as e:
            raise ValueError(f"Failed to load task file: {e}")

        results = {
            "total_tasks": len(tasks.get("subtasks", [])),
            "successful_tasks": 0,
            "failed_tasks": 0,
            "details": []
        }

        for subtask in tasks.get("subtasks", []):
            task_id = subtask.get("id")
            task_desc = subtask.get("description")

            if not task_id or not task_desc:
                results["details"].append({
                    "task_id": task_id,
                    "status": "skipped",
                    "message": "Missing required fields"
                })
                continue

            try:
                result = self._process_single_task(task_desc, task_id)
                results["successful_tasks"] += 1
                status = "completed"
                message = "Task executed successfully"
            except Exception as e:
                results["failed_tasks"] += 1
                status = "failed"
                message = f"Error executing task: {str(e)}"

            results["details"].append({
                "task_id": task_id,
                "status": status,
                "message": message
            })

        if self.verbose:
            print(f"Task execution summary:")
            print(f"- Total tasks: {results['total_tasks']}")
            print(f"- Successful: {results['successful_tasks']}")
            print(f"- Failed: {results['failed_tasks']}")

        return results

    def _process_single_task(self, task_desc: str, task_id: int) -> str:
        """
        Processes a single task through the complete workflow:
        1. Generate initial prompt from task description
        2. Refine prompt using existing refinement workflow
        3. Execute refined prompt using LLM API
        4. Save results to output directory

        Args:
            task_desc (str): Task description text
            task_id (int): Unique identifier for the task

        Returns:
            str: The execution result from the LLM

        Raises:
            Exception: If any step in the processing fails (e.g., file reading,
                       prompt refinement, or API execution errors)

        Side Effects:
            - Modifies conversation history with refined prompts and results
            - Creates output files in the specified directory
            - May produce verbose output if enabled
        """
        if self.verbose:
            print(f"\nProcessing task {task_id}: {task_desc}")

        # Step 1: Generate initial prompt from task description
        initial_prompt = f"Task {task_id}: {task_desc}"

        # Step 2: Refine the prompt using existing refinement workflow
        if self.verbose:
            print(f"Refining and executing prompt for task {task_id}...")

        # Use a generic refinement prompt for task execution
        refinement_prompt_path = f"{Config.DEFAULT_PROMPTS_DIRECTORY}/refine-prompt.md"
        refinement_prompt = FileHelper.read_file(refinement_prompt_path, verbose=self.verbose)

        # Step 3: Execute the refined prompt using LLM API
        execution_result = self.workflow.refine_and_send_prompt(
            input_prompt=initial_prompt,
            refinement_prompt=refinement_prompt,  # No further refinement needed for execution
            refinement_model=self.model,
            execution_model=self.model
        )

        if self.verbose:
            print(f"Execution result for task {task_id}:\n{execution_result}")

        # Step 4: Save the result to output directory
        output_file = f"{self.output_dir}/task_{task_id}_result.md"
        FileHelper.write_to_file(output_file, execution_result, verbose=self.verbose)

        if self.verbose:
            print(f"Result saved to {output_file}")

        return execution_result

if __name__ == "__main__":
    # Example usage
    executor = SequentialTaskExecutor(verbose=True)
    result = executor.execute_tasks_from_file("tasks.json")
    print("\nFinal results:", result)