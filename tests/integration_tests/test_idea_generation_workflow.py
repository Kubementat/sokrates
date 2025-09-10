"""
Integration Test Suite for IdeaGenerationWorkflow

This module contains integration tests that verify the full end-to-end functionality
of the IdeaGenerationWorkflow class. These tests simulate real-world usage scenarios
and validate the workflow's interaction with various components.
"""

import os
import tempfile
from pathlib import Path
import pytest

from sokrates.workflows.idea_generation_workflow import IdeaGenerationWorkflow



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
            topic_input_file="tests/fixtures/topics/science_fiction_games_topic.md",
            verbose=False
        )
        
        content = None
        with open("tests/fixtures/topics/science_fiction_games_topic.md", "r") as file:
          content = file.read()
        
        # Test that the content from file is returned
        result = workflow.generate_or_set_topic()
        assert result == content

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
        assert Path(workflow.output_directory).exists()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])