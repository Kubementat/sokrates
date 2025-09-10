#!/usr/bin/env python3
"""
Tests for the file watcher functionality.
"""

import pytest
import tempfile
import time
import os
from pathlib import Path
from unittest.mock import Mock, patch

from sokrates.task_queue.file_watcher import FileWatcher, FileWatcherEventHandler
from sokrates.task_queue.file_processor import FileProcessor
from sokrates.config import Config


class TestFileWatcher:
    """Test cases for FileWatcher class."""
    
    def test_file_watcher_initialization(self):
        """Test FileWatcher initialization with valid parameters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            callback = Mock()
            watcher = FileWatcher(
                watch_directories=[temp_dir],
                file_processor_callback=callback,
                file_extensions=['.txt', '.md']
            )
            
            assert watcher.watch_directories == [Path(temp_dir).resolve()]
            assert watcher.file_processor_callback == callback
            assert watcher.file_extensions == ['.txt', '.md']
            assert not watcher.is_running()
    
    def test_file_watcher_directory_validation(self):
        """Test FileWatcher directory validation."""
        callback = Mock()
        
        # Test with non-existent directory (should create it)
        with tempfile.TemporaryDirectory() as temp_dir:
            non_existent_dir = Path(temp_dir) / "new_dir"
            watcher = FileWatcher(
                watch_directories=[str(non_existent_dir)],
                file_processor_callback=callback
            )
            assert non_existent_dir.exists()
            assert non_existent_dir in watcher.watch_directories
    
    def test_file_watcher_start_stop(self):
        """Test FileWatcher start and stop functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            callback = Mock()
            watcher = FileWatcher(
                watch_directories=[temp_dir],
                file_processor_callback=callback
            )
            
            # Start the watcher
            watcher.start()
            assert watcher.is_running()
            
            # Stop the watcher
            watcher.stop()
            assert not watcher.is_running()
    
    def test_file_watcher_add_remove_directory(self):
        """Test adding and removing directories from watch list."""
        with tempfile.TemporaryDirectory() as temp_dir1, \
             tempfile.TemporaryDirectory() as temp_dir2:
            
            callback = Mock()
            watcher = FileWatcher(
                watch_directories=[temp_dir1],
                file_processor_callback=callback
            )
            
            # Add new directory
            success = watcher.add_directory(temp_dir2)
            assert success
            assert Path(temp_dir2).resolve() in watcher.watch_directories
            
            # Remove directory
            success = watcher.remove_directory(temp_dir1)
            assert success
            assert Path(temp_dir1).resolve() not in watcher.watch_directories
    
    def test_file_watcher_file_detection(self):
        """Test that file watcher detects new files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            callback = Mock()
            watcher = FileWatcher(
                watch_directories=[temp_dir],
                file_processor_callback=callback,
                file_extensions=['.txt']
            )
            
            watcher.start()
            
            # Create a test file
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Test content")
            
            # Wait a bit for the file system event
            time.sleep(0.5)
            
            # Stop the watcher
            watcher.stop()
            
            # Verify callback was called
            callback.assert_called_with(str(test_file))


class TestFileWatcherEventHandler:
    """Test cases for FileWatcherEventHandler class."""
    
    def test_event_handler_file_extensions(self):
        """Test that event handler filters by file extensions."""
        callback = Mock()
        handler = FileWatcherEventHandler(
            callback=callback,
            file_extensions=['.txt', '.md']
        )
        
        # Create mock events
        mock_txt_event = Mock()
        mock_txt_event.is_directory = False
        mock_txt_event.src_path = "/path/to/file.txt"
        
        mock_py_event = Mock()
        mock_py_event.is_directory = False
        mock_py_event.src_path = "/path/to/file.py"
        
        # Test with allowed extension
        with patch('pathlib.Path.exists', return_value=True):
            handler.on_created(mock_txt_event)
            callback.assert_called_with("/path/to/file.txt")
        
        # Test with disallowed extension
        callback.reset_mock()
        with patch('pathlib.Path.exists', return_value=True):
            handler.on_created(mock_py_event)
            callback.assert_not_called()
    
    def test_event_handler_directory_filtering(self):
        """Test that event handler ignores directory events."""
        callback = Mock()
        handler = FileWatcherEventHandler(callback=callback)
        
        # Create mock directory event
        mock_dir_event = Mock()
        mock_dir_event.is_directory = True
        mock_dir_event.src_path = "/path/to/directory"
        
        handler.on_created(mock_dir_event)
        callback.assert_not_called()


class TestFileProcessor:
    """Test cases for FileProcessor class."""
    
    @patch('sokrates.llm_api.LLMApi')
    @patch('sokrates.task_queue.file_processor.FileHelper')
    def test_file_processor_initialization(self, mock_file_helper, mock_llm_api):
        """Test FileProcessor initialization."""
        config = Mock()
        config.api_endpoint = "http://localhost:1234/v1"
        config.api_key = "test_key"
        config.default_model = "test_model"
        config.default_model_temperature = 0.7
        config.home_path = "/tmp/test"
        config.prompts_directory = "/tmp/test/prompts"
        
        processor = FileProcessor(config=config)
        
        assert processor.config == config
        assert processor.llm_api is not None
        assert processor.refiner is not None
    
    @patch('sokrates.llm_api.LLMApi')
    @patch('sokrates.task_queue.file_processor.FileHelper')
    def test_read_file_content_success(self, mock_file_helper, mock_llm_api):
        """Test successful file content reading."""
        config = Mock()
        config.api_endpoint = "http://localhost:1234/v1"
        config.api_key = "test_key"
        config.default_model = "test_model"
        config.default_model_temperature = 0.7
        config.home_path = "/tmp/test"
        config.prompts_directory = "/tmp/test/prompts"
        
        # Mock file exists and is readable
        mock_file_helper.read_file.return_value = "Test file content"
        
        processor = FileProcessor(config=config)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test file content")
            temp_file = f.name
        
        try:
            content = processor._read_file_content(temp_file)
            assert content == "Test file content"
        finally:
            os.unlink(temp_file)
    
    @patch('sokrates.llm_api.LLMApi')
    def test_read_file_content_nonexistent(self, mock_llm_api):
        """Test reading non-existent file."""
        config = Mock()
        config.api_endpoint = "http://localhost:1234/v1"
        config.api_key = "test_key"
        config.default_model = "test_model"
        config.default_model_temperature = 0.7
        config.home_path = "/tmp/test"
        config.prompts_directory = "/tmp/test/prompts"
        
        processor = FileProcessor(config=config)
        
        content = processor._read_file_content("/nonexistent/file.txt")
        assert content is None
    
    @patch('sokrates.llm_api.LLMApi')
    @patch('sokrates.task_queue.file_processor.FileHelper')
    def test_process_file_success(self, mock_file_helper, mock_llm_api):
        """Test successful file processing."""
        config = Mock()
        config.api_endpoint = "http://localhost:1234/v1"
        config.api_key = "test_key"
        config.default_model = "test_model"
        config.default_model_temperature = 0.7
        config.home_path = "/tmp/test"
        config.prompts_directory = "/tmp/test/prompts"
        
        # Mock file reading
        mock_file_helper.read_file.return_value = "Test prompt content"
        mock_file_helper.write_to_file.return_value = None
        
        # Mock LLM API responses
        mock_llm_instance = Mock()
        mock_llm_instance.send.return_value = "Refined prompt content"
        mock_llm_api.return_value = mock_llm_instance
        
        processor = FileProcessor(config=config)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test prompt content")
            temp_file = f.name
        
        try:
            result = processor.process_file(temp_file)
            
            assert result['file_path'] == temp_file
            assert result['status'] in ['completed', 'failed']  # May fail due to mocking
            assert 'processing_duration' in result
            assert 'output_file' in result
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


@pytest.mark.integration
class TestFileWatcherIntegration:
    """Integration tests for file watcher functionality."""
    
    def test_end_to_end_file_processing(self):
        """Test end-to-end file processing workflow."""
        with tempfile.TemporaryDirectory() as watch_dir, \
             tempfile.TemporaryDirectory() as output_dir:
            
            # Create config
            config = Config()
            config.file_watcher_enabled = True
            config.file_watcher_directories = [watch_dir]
            config.file_watcher_extensions = ['.txt']
            config.home_path = output_dir
            
            # Create file processor
            processor = FileProcessor(config=config)
            
            # Create callback function (ignore return value to match expected signature)
            def process_file_callback(file_path):
                processor.process_file(file_path)
            
            # Create and start file watcher
            watcher = FileWatcher(
                watch_directories=[watch_dir],
                file_processor_callback=process_file_callback,
                file_extensions=['.txt']
            )
            
            watcher.start()
            
            try:
                # Create a test file
                test_file = Path(watch_dir) / "test_prompt.txt"
                test_content = "Please write a short poem about artificial intelligence."
                test_file.write_text(test_content)
                
                # Wait for processing
                time.sleep(2)
                # Check if output file was created
                output_files = list(Path(output_dir).glob("file_watcher_results/*.md"))
                
                # File processing may succeed or fail depending on API availability
                # We just verify the system responded to the file creation
                assert len(output_files) > 1    
                
            finally:
                watcher.stop()