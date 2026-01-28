#!/usr/bin/env python3
"""
Task Queue Database Module

This module provides database access functionality for the task queue system.
It handles SQLite database operations including task management, status tracking,
and history logging using Peewee ORM.

Classes:
    TaskQueueORMDatabase: Manages database connections and CRUD operations for tasks via ORM
"""

from peewee import *
import logging
from typing import List, Dict, Optional
from .orm import db, Task, TaskHistory

class TaskQueueORMDatabase:
    """
    Manages the SQLite database using Peewee ORM for task queue storage and retrieval.

    This class provides methods for adding tasks to the queue, retrieving 
    tasks, updating task status, and logging history changes. It leverages
    Peewee's ORM capabilities for type safety, security, and maintainability.

    Attributes:
        db_path (str): Path to the SQLite database file

    Methods:
        __init__(db_path: str): Initializes the database connection and creates tables
        add_task(): Add a new task to the queue using ORM
        get_all_tasks(): Get all tasks using ORM queries
        get_pending_tasks(): Get pending tasks for processing
        update_task_status(): Update task status with ORM operations
        close(): Close the database connection (handled by Peewee)
    """

    def __init__(self, db_path: str):
        """
        Initializes the TaskQueueORMDatabase with configuration and database setup.

        Args:
            db_path (str): Path to the SQLite database file.
        
        Side Effects:
            - Creates database tables if they don't exist
            - Establishes initial database connection
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info(f"DB Path: {db_path}")
        self.db_path = db_path
        # Initialize Peewee database instance
        self.db = db
        self.db.init(db_path)
        # Create all required tables in the database
        self.db.create_tables([Task, TaskHistory])
        self.connection = self.db.connection

    def add_task(self, description: str, file_path: str,
                 priority: str = "normal") -> Task:
        """Add a new task to the queue using ORM"""
        self.logger.info(f"Adding task with: file_path={file_path}")
        try:
            # Create new task instance with all required fields
            new_task = Task.create(
                description=description,
                file_path=file_path,
                priority=priority
            )
            return new_task

        except IntegrityError as e:
            print(f"Error: Task already exists: {e}")
            raise ValueError(f"Task already exists: {e}")

    def get_task(self, task_id) -> Task:
        self.logger.info("Retrieving task with id: {task_id} ...")
        return Task.select().where(Task.task_id==task_id).get()

    def get_all_tasks(self, limit: Optional[int] = None):
        """Get all tasks using ORM query"""
        self.logger.info("Retrieving all tasks ...")
        query = Task.select()
        if limit is not None:
            query = query.limit(limit)
        return query

    def get_pending_tasks(self, limit: Optional[int] = None) -> List[Dict]:
        """Get pending tasks for processing using ORM"""
        self.logger.info("Retrieving all pending tasks ...")
        query = Task.select().where(Task.status == 'pending')
        if limit is not None:
            query = query.limit(limit)
        return [row for row in query.dicts()]

    def update_task_status(self, task_id: str, status: str,
                           result: Optional[str] = None, error: Optional[str] = None,
                           output_directory: Optional[str] = None) -> None:
        """Update task status with ORM operations and history logging"""

        self.logger.info(f"Updating task status for task with id: {task_id} ...")

        try:
            # Retrieve the task
            task = Task.get(Task.task_id == task_id)
            
            # Update fields directly on model instance
            task.status = status
            task.result = result
            task.error_message = error
            task.output_directory = output_directory
            task.save()
            
            # Log to history table using ORM
            TaskHistory.create(
                task=task,
                status=status,
                result=result,
                error_message=error
            )
        except DoesNotExist:
            print(f"Task {task_id} not found")
            raise ValueError(f"Task {task_id} not found")
        except Exception as e:
            print(f"Failed to update task status: {e}")
            raise
    
    def remove_task(self, task_id: str) -> None:
        """
        Remove a task from the queue.

        Args:
            task_id (str): Unique identifier for the task to remove

        Raises:
            Exception: If database operation fails
        """
        try:
            qry=Task.delete().where(Task.task_id==task_id)
            qry.execute()
        except Exception as e:
            raise Exception(f"Failed to remove task {task_id}: {e}")
        
    def close(self):
        """Close the database connection (handled by Peewee)"""
        db.close()
