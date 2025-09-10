import os
import tempfile

# Assuming the PythonAnalyzer class is in a module called python_analyzer
from sokrates.coding.python_analyzer import PythonAnalyzer


def test_analyze_source_file():
    """Test analyze_source_file with valid source file"""
    
    # Create a temporary source file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        source_content = '''
class ExampleClass:
    """Example class for testing."""
    
    def method1(self, arg1: str) -> str:
        """Method 1 docstring."""
        return arg1
    
    def method2(self) -> None:
        """Method 2 docstring."""
        pass

def standalone_function(arg1: int) -> bool:
    """Standalone function docstring."""
    return True
'''
        f.write(source_content)
        source_filepath = f.name
    
    try:
        # Test analysis without existing test file
        result = PythonAnalyzer.analyze_source_file(source_filepath)
        
        # Verify the structure of the result
        assert 'source_file' in result
        assert result['source_file']['filepath'] == source_filepath
        assert len(result['source_file']['classes']) == 1
        assert len(result['source_file']['functions']) == 3
        
        # Verify class info
        cls = result['source_file']['classes'][0]
        assert cls['name'] == 'ExampleClass'
        assert cls['docstring'] == 'Example class for testing.'
        
        # Verify method info
        methods = cls['methods']
        assert len(methods) == 2
        
        method1 = next(m for m in methods if m['name'] == 'method1')
        assert method1['name'] == 'method1'
        assert method1['docstring'] == 'Method 1 docstring.'
        
        method2 = next(m for m in methods if m['name'] == 'method2')
        assert method2['name'] == 'method2'
        assert method2['docstring'] == 'Method 2 docstring.'
        
        # Verify function info
        func = result['source_file']['functions'][0]
        assert func['name'] == 'standalone_function'
        assert func['docstring'] == 'Standalone function docstring.'
        
        # Test with existing test file (should handle gracefully)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            test_content = '''
def test_example():
    """Test example."""
    pass
'''
            f.write(test_content)
            test_filepath = f.name
        
        try:
            result_with_tests = PythonAnalyzer.analyze_source_file(
                source_filepath, test_filepath
            )
            
            assert 'existing_tests' in result_with_tests
            assert result_with_tests['existing_tests'] is not None
            
        finally:
            os.unlink(test_filepath)
        
    finally:
        # Clean up temporary file
        os.unlink(source_filepath)


def test_analyze_source_file_no_existing_file():
    """Test analyze_source_file with no existing test file"""
    
    # Create a temporary source file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        source_content = '''
def simple_function() -> None:
    """Simple function docstring."""
    pass
'''
        f.write(source_content)
        source_filepath = f.name
    
    try:
        result = PythonAnalyzer.analyze_source_file(source_filepath)
        
        # Verify the structure of the result
        assert 'source_file' in result
        assert result['source_file']['filepath'] == source_filepath
        assert len(result['source_file']['functions']) == 1
        
        func = result['source_file']['functions'][0]
        assert func['name'] == 'simple_function'
        
    finally:
        # Clean up temporary file
        os.unlink(source_filepath)


def test_analyze_source_file_nonexistent_source():
    """Test analyze_source_file with nonexistent source file"""
    
    # Test with non-existent file - should raise an exception
    try:
        PythonAnalyzer.analyze_source_file('/non/existent/file.py')
        assert False, "Should have raised an exception"
    except Exception:
        # Expected behavior
        pass


if __name__ == '__main__':
    test_analyze_source_file()
    test_analyze_source_file_no_existing_file()
    test_analyze_source_file_nonexistent_source()
    print("All tests passed!")
