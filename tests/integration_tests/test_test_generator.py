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
            max_tokens=2000
        )
        
        return generator

    def test_generate_tests_directory(self, sample_files, temp_dir):
        """Test generate_tests with directory path."""
        # Create a test output directory
        output_dir = os.path.join(temp_dir, "output")
         
        generator = TestGenerator(api_endpoint=pytest.TESTING_ENDPOINT, 
                                api_key='notrequired', 
                                model=pytest.TESTING_MODEL,
                                max_tokens=20000)
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
                                max_tokens=20000)
            
        # Call generate_tests
        result = generator.generate_tests(
            file_paths=[os.path.join(sample_files, "sample_module.py")],
            output_dir=output_dir
        )
        
        assert isinstance(result, dict)
        assert "total_files_processed" in result
        assert "tests_generated" in result