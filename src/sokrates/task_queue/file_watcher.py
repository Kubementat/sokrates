#!/usr/bin/env python3
"""
File Watcher Module

This module provides functionality for monitoring directories for new files
and triggering prompt processing workflows when files are detected.
"""

import logging
import threading
import time
from pathlib import Path
from typing import List, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileWatcherEventHandler(FileSystemEventHandler):
    """
    Custom event handler for file system events.
    Processes file creation and modification events.
    """
    
    def __init__(self, callback: Callable[[str], None], 
                 file_extensions: List[str] = None,
                 logger: logging.Logger = None):
        """
        Initialize the event handler.
        
        Args:
            callback: Function to call when a relevant file event occurs
            file_extensions: List of file extensions to process (e.g., ['.txt', '.md'])
            logger: Logger instance for logging events
        """
        self.callback = callback
        self.file_extensions = file_extensions or ['.txt', '.md']
        self.logger = logger or logging.getLogger(__name__)
        
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            self._process_file_event(event.src_path, "created")
            
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            self._process_file_event(event.src_path, "modified")
            
    def _process_file_event(self, file_path: str, event_type: str):
        """
        Process a file system event.
        
        Args:
            file_path: Path to the file that triggered the event
            event_type: Type of event ('created' or 'modified')
        """
        try:
            # Check if file extension is in our allowed list
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.file_extensions:
                self.logger.debug(f"Ignoring {event_type} event for file {file_path} - extension not in allowed list")
                return
                
            # Check if file exists and is readable
            if not Path(file_path).exists():
                self.logger.warning(f"File {file_path} reported in {event_type} event but does not exist")
                return
                
            self.logger.info(f"File {event_type}: {file_path}")
            self.callback(file_path)
            
        except Exception as e:
            self.logger.error(f"Error processing {event_type} event for file {file_path}: {e}")

class FileWatcher:
    """
    File system watcher for monitoring directories and processing new files.
    
    This class uses the watchdog library to monitor specified directories for
    file creation and modification events, then processes detected files
    through the provided callback function.
    """
    
    def __init__(self, watch_directories: List[str], 
                 file_processor_callback: Callable[[str], None],
                 file_extensions: List[str] = None,
                 logger: logging.Logger = None):
        """
        Initialize the FileWatcher.
        
        Args:
            watch_directories: List of directory paths to monitor
            file_processor_callback: Function to call when a new file is detected
            file_extensions: List of file extensions to process (default: ['.txt', '.md'])
            logger: Logger instance for logging events
        """
        self.watch_directories = [Path(d).resolve() for d in watch_directories]
        self.file_processor_callback = file_processor_callback
        self.file_extensions = file_extensions or ['.txt', '.md']
        self.logger = logger or logging.getLogger(__name__)
        
        self.observer = None
        self.event_handler = None
        self.running = False
        self.thread = None
        
        # Validate watch directories
        self._validate_directories()
        
    def _validate_directories(self):
        """Validate that watch directories exist and are accessible."""
        for directory in self.watch_directories:
            if not directory.exists():
                self.logger.warning(f"Watch directory {directory} does not exist, creating it")
                try:
                    directory.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    self.logger.error(f"Failed to create watch directory {directory}: {e}")
                    raise
                    
            if not directory.is_dir():
                raise ValueError(f"Watch path {directory} is not a directory")
                
            # Check if directory is readable by trying to list it
            try:
                directory.iterdir()
            except PermissionError:
                raise ValueError(f"Watch directory {directory} is not readable")
                
    def start(self):
        """Start the file watcher."""
        if self.running:
            self.logger.warning("File watcher is already running")
            return
            
        self.logger.info(f"Starting file watcher for directories: {self.watch_directories}")
        
        # Create event handler
        self.event_handler = FileWatcherEventHandler(
            callback=self.file_processor_callback,
            file_extensions=self.file_extensions,
            logger=self.logger
        )
        
        # Create and start observer
        self.observer = Observer()
        
        for directory in self.watch_directories:
            self.observer.schedule(self.event_handler, str(directory), recursive=True)
            self.logger.info(f"Monitoring directory: {directory}")
            
        # Start observer in a separate thread
        self.thread = threading.Thread(target=self._run_observer, daemon=True)
        self.thread.start()
        self.running = True
        
        self.logger.info("File watcher started successfully")
        
    def _run_observer(self):
        """Run the observer in a separate thread."""
        try:
            self.observer.start()
            # Keep the observer running
            while self.running:
                time.sleep(1)
        except Exception as e:
            self.logger.error(f"Error in file watcher observer: {e}")
        finally:
            if self.observer:
                self.observer.stop()
                self.observer.join()
                
    def stop(self):
        """Stop the file watcher."""
        if not self.running:
            self.logger.warning("File watcher is not running")
            return
            
        self.logger.info("Stopping file watcher")
        self.running = False
        
        # Wait for the observer thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
            
        self.logger.info("File watcher stopped")
        
    def is_running(self) -> bool:
        """Check if the file watcher is running."""
        return self.running
        
    def get_watched_directories(self) -> List[Path]:
        """Get the list of directories being watched."""
        return self.watch_directories.copy()
        
    def add_directory(self, directory: str) -> bool:
        """
        Add a new directory to watch.
        
        Args:
            directory: Path to the directory to add
            
        Returns:
            bool: True if directory was added successfully, False otherwise
        """
        try:
            directory_path = Path(directory).resolve()
            
            if directory_path in self.watch_directories:
                self.logger.warning(f"Directory {directory} is already being watched")
                return False
                
            if not directory_path.exists():
                directory_path.mkdir(parents=True, exist_ok=True)
                
            if not directory_path.is_dir():
                self.logger.error(f"Path {directory} is not a directory")
                return False
                
            self.watch_directories.append(directory_path)
            
            # If watcher is running, add the new directory to the observer
            if self.running and self.observer:
                self.observer.schedule(self.event_handler, str(directory_path), recursive=True)
                self.logger.info(f"Added directory to watch list: {directory_path}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add directory {directory}: {e}")
            return False
            
    def remove_directory(self, directory: str) -> bool:
        """
        Remove a directory from the watch list.
        
        Args:
            directory: Path to the directory to remove
            
        Returns:
            bool: True if directory was removed successfully, False otherwise
        """
        try:
            directory_path = Path(directory).resolve()
            
            if directory_path not in self.watch_directories:
                self.logger.warning(f"Directory {directory} is not being watched")
                return False
                
            self.watch_directories.remove(directory_path)
            
            # If watcher is running, we need to restart it to remove the directory
            if self.running:
                self.logger.info(f"Removing directory from watch list: {directory_path}")
                self.logger.info("Restarting file watcher to apply changes")
                self.stop()
                self.start()
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove directory {directory}: {e}")
            return False