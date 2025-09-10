import os
import tempfile
import shutil

import pytest

# Import the actual class to test (assuming it's in a package structure)
from sokrates.coding.test_generator import TestGenerator  # Replace 'your_package' with actual module path


class TestTestGenerator:
    """Integration tests for TestGenerator class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir)

    @pytest.fixture
    def sample_files(self, temp_dir):
        """Create sample Python files in a temporary directory."""
        # Create a simple module file
        module_content = '''
def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract b from a."""
    return a - b

class Calculator:
    def multiply(self, x, y):
        """Multiply two numbers."""
        return x * y
'''
        
        module_path = os.path.join(temp_dir, "sample_module.py")
        with open(module_path, 'w') as f:
            f.write(module_content)
            
        # Create a more complex module file
        complex_content = '''
def process_data(data):
    """Process data and return result."""
    if not isinstance(data, list):
        raise ValueError("Expected list of items")
    
    result = []
    for item in data:
        if isinstance(item, int):
            result.append(item * 2)
        else:
            result.append(str(item))
    return result

def calculate_average(numbers):
    """Calculate average of numbers."""
    try:
        total = sum(numbers)
        count = len(numbers)
        return total / count
    except ZeroDivisionError:
        return 0.0
'''
        
        complex_path = os.path.join(temp_dir, "complex_module.py")
        with open(complex_path, 'w') as f:
            f.write(complex_content)

        yield temp_dir

    @pytest.fixture
    def test_generator(self):
        """Create a TestGenerator instance for testing."""
        # Create mock API that simulates real behavior without external calls
        generator = TestGenerator(
            api_endpoint=pytest.TESTING_ENDPOINT,
            api_key='notrequired',
            model=pytest.TESTING_MODEL,
            temperature=0.7,
            max_tokens=2000,
            verbose=False
        )
        
        return generator

    def test_generate_tests_directory(self, sample_files, temp_dir):
        """Test generate_tests with directory path."""
        # Create a test output directory
        output_dir = os.path.join(temp_dir, "output")
         
        generator = TestGenerator(api_endpoint=pytest.TESTING_ENDPOINT, 
                                api_key='notrequired', 
                                model=pytest.TESTING_MODEL,
                                max_tokens=20000,
                                verbose=False)
        # Call generate_tests
        result = generator.generate_tests(
            directory_path=sample_files,
            output_dir=output_dir
        )
                
        assert isinstance(result, dict)
        assert "total_files_processed" in result
        assert "tests_generated" in result
        assert len(result['files_created']) == 2

    def test_generate_tests_file_paths(self, sample_files, temp_dir):
        """Test generate_tests with specific file paths."""
        output_dir = os.path.join(temp_dir, "output")

        generator = TestGenerator(api_endpoint=pytest.TESTING_ENDPOINT, 
                                api_key='notrequired', 
                                model=pytest.TESTING_MODEL, 
                                max_tokens=20000,
                                verbose=False)
            
        # Call generate_tests
        result = generator.generate_tests(
            file_paths=[os.path.join(sample_files, "sample_module.py")],
            output_dir=output_dir
        )
        
        assert isinstance(result, dict)
        assert "total_files_processed" in result
        assert "tests_generated" in result

#     def test_generate_tests_invalid_input(self):
#         """Test generate_tests with invalid input."""
#         generator = TestGenerator(model="test-model", verbose=False)
        
#         # This should raise ValueError since neither directory_path nor file_paths is specified
#         with pytest.raises(ValueError, match="Either directory_path or file_paths must be specified"):
#             generator.generate_tests(output_dir="./tests")

#     def test_generate_tests_with_existing_test_files(self, sample_files, temp_dir):
#         """Test generate_tests when existing test files exist."""
#         output_dir = os.path.join(temp_dir, "output")
        
#         # Create a mock response
#         mock_response = '''def test_add():
#     assert add(1, 2) == 3

# def test_subtract():
#     assert subtract(5, 3) == 2
# '''
        
#         with patch.object(TestGenerator, '_prepare_source_files') as mock_prepare:
#             # Mock the file preparation to return our sample files
#             mock_prepare.return_value = [
#                 os.path.join(sample_files, "sample_module.py")
#             ]
            
#             generator = TestGenerator(model="test-model", verbose=False)
            
#             with patch.object(generator.llm_api, 'send') as mock_send:
#                 mock_send.return_value = mock_response
                
#                 # Call generate_tests
#                 result = generator.generate_tests(
#                     file_paths=[os.path.join(sample_files, "sample_module.py")],
#                     output_dir=output_dir
#                 )
                
#                 assert isinstance(result, dict)
#                 assert result['total_files_processed'] == 1

#     def test_generate_tests_with_strategy(self, sample_files, temp_dir):
#         """Test generate_tests with custom strategy."""
#         output_dir = os.path.join(temp_dir, "output")
        
#         # Create a mock response
#         mock_response = '''def test_add():
#     assert add(1, 2) == 3

# def test_process_data():
#     result = process_data([1, 2, 3])
#     assert result == [2, 4, 6]
# '''
        
#         with patch.object(TestGenerator, '_prepare_source_files') as mock_prepare:
#             # Mock the file preparation to return our sample files
#             mock_prepare.return_value = [
#                 os.path.join(sample_files, "sample_module.py")
#             ]
            
#             generator = TestGenerator(model="test-model", verbose=False)
            
#             with patch.object(generator.llm_api, 'send') as mock_send:
#                 mock_send.return_value = mock_response
                
#                 # Call generate_tests
#                 result = generator.generate_tests(
#                     file_paths=[os.path.join(sample_files, "sample_module.py")],
#                     output_dir=output_dir,
#                     strategy="base"
#                 )
                
#                 assert isinstance(result, dict)

#     def test_get_available_strategies(self):
#         """Test that get_available_strategies returns expected values."""
#         generator = TestGenerator(model="test-model", verbose=False)
        
#         strategies = generator.get_available_strategies()
#         expected_strategies = ["base", "edge_cases", "error_handling", "validation"]
        
#         assert isinstance(strategies, list)
#         for strategy in expected_strategies:
#             assert strategy in strategies

#     def test_set_custom_strategy(self):
#         """Test setting a custom strategy."""
#         generator = TestGenerator(model="test-model", verbose=False)
        
#         # Create a dummy template path
#         dummy_template = "/dummy/path/template.md"
        
#         # This should not raise any error
#         generator.set_custom_strategy("custom_strategy", dummy_template)
        
#         assert "custom_strategy" in generator.prompt_templates

#     def test_prepare_source_files_directory(self, sample_files):
#         """Test _prepare_source_files with directory path."""
#         generator = TestGenerator(model="test-model", verbose=False)
        
#         files = generator._prepare_source_files(directory_path=sample_files)
        
#         # Should return list of Python files (excluding test files and __init__.py)
#         assert isinstance(files, list)
#         for f in files:
#             assert f.endswith('.py')

#     def test_prepare_source_files_file_paths(self, sample_files):
#         """Test _prepare_source_files with specific file paths."""
#         generator = TestGenerator(model="test-model", verbose=False)
        
#         file_path = os.path.join(sample_files, "sample_module.py")
#         files = generator._prepare_source_files(file_paths=[file_path])
        
#         assert isinstance(files, list)
#         assert len(files) == 1
#         assert file_path in files

#     def test_build_test_generation_prompt(self, sample_files):
#         """Test _build_test_generation_prompt method."""
#         generator = TestGenerator(model="test-model", verbose=False)
        
#         # Mock the analysis result to avoid actual analyzer calls
#         mock_analysis_result = {
#             'source_file': {
#                 'filepath': os.path.join(sample_files, "sample_module.py"),
#                 'functions': [
#                     {'name': 'add', 'args': [{'name': 'a'}, {'name': 'b'}], 'return_type': 'int'},
#                     {'name': 'subtract', 'args': [{'name': 'a'}, {'name': 'b'}], 'return_type': 'int'}
#                 ]
#             }
#         }
        
#         # Create a basic template
#         template = "Module: {{module_name}}\nFunctions to test: {{function_count}}"
        
#         prompt = generator._build_test_generation_prompt(template, mock_analysis_result)
        
#         assert "sample_module" in prompt or "{{module_name}}" not in prompt  # Template should be substituted
        
#     def test_clean_generated_code(self):
#         """Test _clean_generated_code method."""
#         generator = TestGenerator(model="test-model", verbose=False)
        
#         raw_code = '''
# ```python
# def test_example():
#     assert True
# ```
# '''
#         cleaned = generator._clean_generated_code(raw_code)
#         # Should have proper formatting
#         assert isinstance(cleaned, str)
#         assert "def test_example" in cleaned