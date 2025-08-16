"""
Integration Test Suite for IdeaGenerationWorkflow

This module contains integration tests that verify the full end-to-end functionality
of the IdeaGenerationWorkflow class. These tests simulate real-world usage scenarios
and validate the workflow's interaction with various components.
"""

import os
import tempfile
import json
from pathlib import Path
import pytest
from unittest.mock import Mock, patch

# Import the IdeaGenerationWorkflow class from src.sokrates.idea_generation_workflow
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from sokrates.idea_generation_workflow import IdeaGenerationWorkflow
from sokrates.config import Config
import pytest


class TestIdeaGenerationWorkflowIntegration:
    """Integration tests for the IdeaGenerationWorkflow class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for output files
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock the API endpoint and key to avoid actual LLM calls during testing
        self.api_endpoint = pytest.TESTING_ENDPOINT
        self.api_key = "test_api_key"

    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def test_full_workflow(self):
      workflow = IdeaGenerationWorkflow(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key,
            topic="The beauty of planet Earth as seen from space.",
            verbose=True,
            idea_count=3
        )
      list = workflow.run()
      assert len(list) == 3

    def test_generate_or_set_topic_with_input_file(self):
        """Test topic generation when a topic input file is provided."""
        
        workflow = IdeaGenerationWorkflow(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key,
            topic_input_file="tests/topics/science_fiction_games_topic.md",
            verbose=False
        )
        
        content = None
        with open("tests/topics/science_fiction_games_topic.md", "r") as file:
          content = file.read()
        
        # Test that the content from file is returned
        result = workflow.generate_or_set_topic()
        assert result == content

    def test_execute_prompt_generation(self):
        """Test prompt generation functionality."""

        workflow = IdeaGenerationWorkflow(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key,
            idea_count=2,
            output_directory=self.temp_dir,
            verbose=False
        )
        
        # Test that prompts are generated correctly
        result = workflow.execute_prompt_generation()
        
        assert len(result) == 2

    def test_refine_and_execute_prompt(self):
        """Test the refine and execute prompt functionality."""
        
        workflow = IdeaGenerationWorkflow(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key,
            verbose=False
        )
        
        # Test that the prompt is refined and executed correctly
        result = workflow.refine_and_execute_prompt("Test prompt", 1)
        
        assert len(result) > 0

    @patch('src.sokrates.idea_generation_workflow.FileHelper.read_file')
    @patch('src.sokrates.idea_generation_workflow.FileHelper.read_json_file')
    @patch('src.sokrates.idea_generation_workflow.Utils.generate_random_int')
    @patch('src.sokrates.idea_generation_workflow.OutputPrinter.print_info')
    def test_run_method_with_mocked_components(self, mock_print, mock_rand_int, mock_read_json, mock_read_file):
        """Test the full run method with mocked components."""
        # Setup mocks
        mock_read_file.side_effect = [
            "Generate a topic about:",  # Topic generator instructions  
            "Generate prompts based on topic:",  # Prompt generator template
            "Refinement instructions"   # Refinement prompt file
        ]
        mock_read_json.return_value = {"topic_categories": ["Technology", "Science"]}
        mock_rand_int.side_effect = [2, 1]  # Category picking and index
        
        workflow = IdeaGenerationWorkflow(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key,
            idea_count=1,
            output_directory=self.temp_dir,
            verbose=False
        )
        
        # Mock all the components that would normally make API calls
        workflow.generate_or_set_topic = Mock(return_value="Test Topic")
        workflow.execute_prompt_generation = Mock(return_value=["Test Prompt"])
        workflow.refine_and_execute_prompt = Mock(return_value="Final Result")
        
        # Test that run method executes without errors
        result = workflow.run()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == "Final Result"

    def test_workflow_initialization_with_defaults(self):
        """Test that the workflow initializes correctly with default parameters."""
        workflow = IdeaGenerationWorkflow(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key,
            verbose=False
        )
        
        # Check that all attributes are properly set
        assert hasattr(workflow, 'api_endpoint')
        assert hasattr(workflow, 'api_key') 
        assert hasattr(workflow, 'llm_api')
        assert hasattr(workflow, 'prompt_refiner')
        assert hasattr(workflow, 'topic')
        assert hasattr(workflow, 'topic_input_file')
        assert hasattr(workflow, 'output_directory')
        assert hasattr(workflow, 'max_tokens')
        assert hasattr(workflow, 'temperature')
        assert hasattr(workflow, 'verbose')
        
        # Check default values
        assert workflow.api_endpoint == self.api_endpoint
        assert workflow.api_key == self.api_key
        assert workflow.idea_count == 2
        assert workflow.max_tokens == 20000
        assert workflow.temperature == 0.7

    def test_workflow_initialization_with_custom_parameters(self):
        """Test that the workflow initializes correctly with custom parameters."""
        workflow = IdeaGenerationWorkflow(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key,
            topic="Custom Topic",
            idea_count=5,
            max_tokens=10000,
            temperature=0.9,
            verbose=True
        )
        
        # Check that custom values are properly set
        assert workflow.topic == "Custom Topic"
        assert workflow.idea_count == 5
        assert workflow.max_tokens == 10000
        assert workflow.temperature == 0.9
        assert workflow.verbose is True

    def test_pick_topic_categories_from_json(self):
        """Test the topic category picking functionality."""
        # This would normally read from a JSON file, but we're testing just the logic
        
        workflow = IdeaGenerationWorkflow(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key,
            verbose=False
        )
        
        # Mock the FileHelper.read_json_file to return test data
        with patch('sokrates.idea_generation_workflow.FileHelper.read_json_file') as mock_read:
            mock_read.return_value = {"topic_categories": ["Technology", "Science", "Art", "Music", "Sports"]}
            
            categories = workflow.pick_topic_categories_from_json()
            
            # Should return a list of categories
            assert isinstance(categories, list)
            assert len(categories) >= 1
            assert len(categories) <= workflow.MAXIMUM_CATEGORIES_TO_PICK
            
            # All returned items should be from the available categories
            for category in categories:
                assert category in ["Technology", "Science", "Art", "Music", "Sports"]

    def test_workflow_with_output_directory(self):
        """Test that output directory handling works correctly."""
        workflow = IdeaGenerationWorkflow(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key,
            output_directory=self.temp_dir,
            verbose=False
        )
        
        # Check that the output directory is set properly
        assert workflow.output_directory == self.temp_dir

if __name__ == "__main__":
    pytest.main([__file__, "-v"])