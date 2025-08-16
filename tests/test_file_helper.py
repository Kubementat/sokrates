import pytest
from pathlib import Path
from sokrates import FileHelper

import shutil

from unittest.mock import patch
import pytest

@pytest.fixture
def tmp_path(tmp_path):
    yield tmp_path
    shutil.rmtree(tmp_path)

class TestFileHelperBasicFunctionality:

    def test_create_new_file(self, tmp_path):
        test_file = tmp_path / "test.txt"
        assert not test_file.exists()
        FileHelper.create_new_file(test_file)
        assert test_file.exists()
        
    def test_write_to_file(self, tmp_path):
        content = "Hello, world!"
        test_file = tmp_path / "content.txt"
        FileHelper.write_to_file(file_path=test_file, content=content)
        assert test_file.read_text() == content
        
    def test_read_file(self, tmp_path):
        test_file = tmp_path / "test.txt"
        FileHelper.create_new_file(test_file)
        expected_content = "Sample content."
        FileHelper.write_to_file(file_path=test_file, content=expected_content)
        actual_content = FileHelper.read_file(test_file)
        assert actual_content == expected_content
    
    def test_create_and_return_task_execution_directory_with_custom_path(self, tmp_path):
        """Test creating task execution directory with custom path."""
        custom_dir = tmp_path / "custom_output"
        
        # Mock the Path.mkdir method to track calls
        with patch('src.sokrates.file_helper.Path.mkdir') as mock_mkdir:
            result = FileHelper.create_and_return_task_execution_directory(str(custom_dir))
            
            # Check that it returns the correct path
            assert result == str(custom_dir)
            # Check that mkdir was called for custom directory
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_create_and_return_task_execution_directory_default_path(self, tmp_path):
        """Test creating task execution directory with default path."""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        # Mock datetime.now() to return a fixed time
        mock_datetime = '2023-01-01_12-00'
        with patch('src.sokrates.file_helper.datetime') as mock_dt:
            mock_dt.now.return_value.strftime.return_value = mock_datetime
            
            with patch('src.sokrates.file_helper.Path.home', return_value=home_dir):
                # Mock the Path.mkdir method to track calls
                with patch('src.sokrates.file_helper.Path.mkdir') as mock_mkdir:
                    result = FileHelper.create_and_return_task_execution_directory()
                    
                    expected_path = str(home_dir / ".sokrates" / "tasks" / "results" / "2023-01-01_12-00")
                    assert str(result) == expected_path
                    
                    # Check that mkdir was called for the default directory
                    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


class TestFileHelperEdgeCases:
    def test_write_to_existing_file(self, tmp_path):
        test_file = tmp_path / "test.txt"
        initial_content = "First line."
        FileHelper.write_to_file(file_path=test_file, content=initial_content)
        new_content = "Second line."
        FileHelper.write_to_file(file_path=test_file, content=new_content)
        assert test_file.read_text() == new_content
