#!/usr/bin/env python3
"""
Task Queue Manager Module

This module provides the main interface for managing the task queue system.
It handles adding tasks, retrieving pending tasks, and updating task status.

Classes:
    TaskQueueManager: Manages task queue operations with database integration
"""
from typing import List, Dict, Optional
from .database import TaskQueueORMDatabase
from sokrates.config import Config
from sokrates.task_queue.orm import Task

class TaskQueueManager:

    def __init__(self, config: Config):
        """
        Initializes the TaskQueueManager with database configuration.

        Args:
            db_path (str, optional): Path to the SQLite database file.
                If None, uses the default from TaskQueueORMDatabase.
        """
        self.config = config
        self.db = TaskQueueORMDatabase(self.config.get('database_path'))

    def get_task(self, task_id) -> Task:
        return self.db.get_task(task_id=task_id)

    def add_task_from_file(self, task_file_path: str,
                          priority: str = "normal") -> str:
        """
        Add a new task from JSON file to the queue.

        Args:
            task_file_path (str): Path to the JSON file containing task definition
            priority (str, optional): Task priority level. Defaults to "normal".

        Returns:
            str: The generated task ID

        Raises:
            ValueError: If task file cannot be loaded or parsed
            Exception: If database operation fails
        """
        try:
            new_task = self.db.add_task(
                description = "Task from JSON file",
                file_path=task_file_path,
                priority=priority
            )
            
            return str(new_task.task_id)

        except Exception as e:
            raise ValueError(f"Failed to add task from {task_file_path}: {e}")

    def get_all_tasks(self, limit: Optional[int] = None):
        """
        Get all tasks for processing.

        Args:
            limit (int, optional): Maximum number of tasks to return. If None, returns all.
        """
        try:
            return self.db.get_all_tasks(limit)
        except Exception as e:
            raise Exception(f"Failed to retrieve all tasks: {e}")

    def get_pending_tasks(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get pending tasks for processing.

        Args:
            limit (int, optional): Maximum number of tasks to return. If None, returns all.

        Returns:
            List[Dict]: List of task dictionaries with pending status
        """
        try:
            return self.db.get_pending_tasks(limit)
        except Exception as e:
            raise Exception(f"Failed to retrieve pending tasks: {e}")

    def update_task_status(self, task_id: str, status: str,
                          result: Optional[str] = None, error: Optional[str] = None,
                          output_directory: Optional[str] = None) -> None:
        """
        Update task status with optional result/error.

        Args:
            task_id (str): Unique identifier for the task
            status (str): New status for the task
            result (str, optional): Execution result if completed
            error (str, optional): Error message if failed
            output_directory (str, optional): Output directory of the task

        Raises:
            Exception: If database operation fails
        """
        try:
            self.db.update_task_status(task_id=task_id, 
                status=status, result=result, 
                error=error, output_directory=output_directory)
        except Exception as e:
            raise Exception(f"Failed to update task status for {task_id}: {e}")

    def remove_task(self, task_id: str) -> None:
        self.db.remove_task(task_id=task_id)

    def close(self):
        """
        Closes the underlying database connection.

        This method ensures that all database resources are properly closed
        and released. It should be called when the TaskQueueManager is no longer needed.
        
        Returns:
            None
        """
        self.db.close()

    def __enter__(self):
        """Support context manager protocol"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support context manager protocol"""
        self.close()
