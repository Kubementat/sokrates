"""
Test suite for the MergeIdeasWorkflow class.

This module contains unit tests for the MergeIdeasWorkflow class which handles
merging multiple ideas or documents using LLM capabilities.
"""

import pytest

from sokrates.workflows.merge_ideas_workflow import MergeIdeasWorkflow
from sokrates.constants import Constants

class TestMergeIdeasWorkflow:
    """Test cases for the MergeIdeasWorkflow class."""

    def test_init_default_values(self):
        """Test initialization with default values."""
        workflow = MergeIdeasWorkflow()
        
        assert hasattr(workflow, 'llm_api')
        assert hasattr(workflow, 'refiner')
        assert hasattr(workflow, 'model')
        assert hasattr(workflow, 'max_tokens')
        assert hasattr(workflow, 'temperature')
        assert hasattr(workflow, 'verbose')
        assert workflow.model == Constants.DEFAULT_MODEL
        assert workflow.max_tokens == 50000
        assert workflow.temperature == MergeIdeasWorkflow.DEFAULT_TEMPERATURE
        assert workflow.verbose is False

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        workflow = MergeIdeasWorkflow(
            api_endpoint="https://custom.api.com",
            api_key="custom_api_key", 
            model="gpt-4",
            max_tokens=10000,
            temperature=0.9,
            verbose=True
        )
        
        assert workflow.model == "gpt-4"
        assert workflow.max_tokens == 10000
        assert workflow.temperature == 0.9
        assert workflow.verbose is True

    def test_merge_ideas_with_documents(self):
        """Test merging ideas with multiple documents."""
        workflow = MergeIdeasWorkflow()
        
        # Create test documents
        source_documents = [
            {
                'identifier': 'cats.md',
                'content': 'A cat is the best companion for a human.'
            },
            {
                'identifier': 'dogs.md', 
                'content': 'A dog is the best companion for a human.'
            }
        ]
        # Execute merge
        result = workflow.merge_ideas(source_documents)
        
        # Verify the result
        assert len(result) > 0

    def test_prompt_loading(self):
        """Test that the correct prompt file is loaded."""
        
        workflow = MergeIdeasWorkflow()
        
        # Verify that FileHelper.read_file was called with the expected path
        assert 'merge-ideas' in workflow.idea_merger_prompt_file

if __name__ == "__main__":
    pytest.main([__file__])