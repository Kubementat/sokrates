# Coding Conventions

This document defines the coding style, naming conventions, architectural patterns, and development standards for Sokrates. These conventions ensure consistency, readability, and maintainability across the codebase.

---

## Python Version Requirements

- **Minimum Version**: Python 3.9+
- **Modern Type Hints**: Use built-in collection types (`list[str]`, `dict[str, Any]`) instead of `typing` module aliases
- **F-strings**: Required for string formatting (Python 3.6+)

---

## Import Conventions

### Import Order

Imports must be ordered in three distinct groups, separated by blank lines:

1. **Standard Library** (Python built-in modules)
2. **Third-Party** (external packages from PyPI)
3. **Local/Relative** (sokrates package imports and relative imports within the same package)

### Example Import Structure

```python
# Standard library
import os
from pathlib import Path
from typing import Any, Optional

# Third-party
import click
from openai import OpenAI
from peewee import Model, SqliteDatabase

# Local imports (absolute for public modules)
from sokrates.file_helper import FileHelper
from sokrates.llm_api import LLMApi

# Relative imports within package (used in same package)
from .module import helper_function
from .local_module import LocalClass
```

### Import Best Practices

- Use **absolute imports** for public modules: `from sokrates.module import Class`
- Use **relative imports** only within the same package: `from .module import Function`
- Avoid wildcard imports (`from module import *`)
- Import specific names rather than entire modules when possible

---

## Naming Conventions

### General Rules

| Element | Convention | Example |
|---------|------------|---------|
| **Classes** | PascalCase | `LLMApi`, `FileHelper` |
| **Functions/Methods** | snake_case | `list_models()`, `read_file()` |
| **Variables** | snake_case | `api_endpoint`, `file_path` |
| **Constants** | UPPERCASE_SNAKE_CASE | `DEFAULT_API_ENDPOINT`, `MAX_TOKENS` |
| **Private Members** | Single underscore prefix | `_internal_cache`, `_validate_input()` |

### File and Module Naming

- **Module files**: lowercase_with_underscores.py (e.g., `llm_api.py`, `file_helper.py`)
- **Package directories**: lowercase without underscores (e.g., `cli/`, `workflows/`)
- **Test files**: test_module_name.py pattern (e.g., `test_llm_api.py`)

### Avoid Naming Conflicts

- Do not use single-character names except for loop variables (`i`, `j`, `k`) or throwaway variables (`_`)
- Avoid names that shadow built-in functions (`list`, `dict`, `str`, etc.)
- Use descriptive names that convey purpose and type

---

## Code Style Standards

### Line Length

- **Maximum**: 120 characters per line
- **Preferred**: Keep lines under 88 characters when possible
- **Violations**: Break long strings or method chains at logical boundaries

### String Quotes

- **Default**: Single quotes (`'text'`) for all string literals
- **Exception**: Use double quotes (`"text"`) when the string contains single quotes: `"It's a test"`
- **Docstrings**: Triple single quotes (`'''docstring'''`)

### Whitespace and Formatting

- **One blank line** between top-level definitions (functions, classes)
- **Two blank lines** before class definitions
- **No trailing whitespace** on any line
- **Unix-style line endings** (LF, not CRLF)
- **File ends with newline**

### Type Hints

```python
# Required for all function signatures and class attributes
def process_data(input: str, config: Optional[dict[str, Any]] = None) -> dict[str, int]:
    """Process input data and return metrics.
    
    Args:
        input: The input string to process
        config: Optional configuration dictionary
        
    Returns:
        Dictionary mapping metric names to integer values
    """
    pass

# Class attributes should be typed in __init__ or as class variables
class Config:
    DEFAULT_TIMEOUT: int = 30
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.timeout: int = timeout
```

### F-Strings

Use f-strings for all string interpolation (Python 3.6+ required):

```python
# Preferred
result = f"Processed {count} items in {duration}s"

# Avoid using .format() or % formatting
result = "Processed {} items in {}s".format(count, duration)
```

---

## Documentation Standards

### Docstrings

All public classes and functions must have docstrings following **Google style format**:

```python
class MyClass:
    """Short description.
    
    Extended description can span multiple lines.
    
    Args:
        param1: Description of the first parameter
        param2: Description of the second parameter
        
    Returns:
        Description of return value and type
        
    Raises:
        ExceptionType: When this exception is raised with explanation
        
    Example:
        >>> obj = MyClass()
        >>> obj.do_something()
        'result'
    """
    
    def method(self, arg1: str) -> bool:
        """Method short description.
        
        Extended description if needed.
        
        Args:
            arg1: Parameter description
            
        Returns:
            Return value description
        """
```

### Module-Level Docstrings

Each module must begin with a docstring explaining its purpose:

```python
"""LLM interaction interface supporting any OpenAI-compatible endpoint.

This module provides the LLMApi class which abstracts LLM interactions,
handles streaming responses, and tracks performance metrics.
"""
```

---

## Error Handling Standards

### Exception Philosophy

1. **Raise specific exceptions** with descriptive messages indicating context
2. **Log errors before raising** when appropriate using `logging.getLogger(__name__)`
3. **Handle expected failures gracefully** without crashing (e.g., file watcher errors)
4. **Use try/except only when meaningful handling is possible**

### Raising Exceptions

```python
# Preferred: Specific exception with context
if not file_path.exists():
    raise FileNotFoundError(f"Configuration file not found: {file_path}")

if temperature < 0 or temperature > 1:
    raise ValueError(f"Temperature must be between 0 and 1, got: {temperature}")

# Avoid generic exceptions unless truly unexpected
try:
    result = risky_operation()
except Exception as e:
    logger.error("Unexpected error in operation", exc_info=True)
    raise RuntimeError("Operation failed") from e
```

### Error Logging

Use the module-level logger for all error reporting:

```python
import logging

logger = logging.getLogger(__name__)

def process_file(file_path: Path):
    try:
        content = file_path.read_text(encoding='utf-8')
    except FileNotFoundError as e:
        logger.error(f"File not found during processing: {file_path}")
        raise
    except PermissionError as e:
        logger.warning(f"Permission denied for file: {file_path}")
```

---

## File Operations Standards

### Path Handling

Always use `pathlib.Path` instead of `os.path`:

```python
from pathlib import Path

# Preferred
config_file = Path.home() / ".sokrates" / "config.yml"

# Avoid
import os
config_file = os.path.join(os.environ['HOME'], '.sokrates', 'config.yml')
```

### File Operations

- **Always specify encoding**: `encoding='utf-8'` for all text file operations
- **Create parent directories automatically** when writing files: `Path.mkdir(parents=True, exist_ok=True)`
- **Use context managers** for file operations: `with open(path) as f:`
- **Log file operations at debug level**: `logger.debug(f"Read file: {file_path}")`

### File Helper Pattern

Use the centralized `FileHelper` class for common file system operations to ensure consistency:

```python
from sokrates.file_helper import FileHelper

helper = FileHelper()
content = helper.read_file(file_path)  # Consistent error handling
helper.write_to_file(output_path, content)  # Auto-creates directories
```

---

## Architectural Patterns

### Dependency Injection

Use constructor injection for all dependencies to enable testability:

```python
class RefinementWorkflow:
    def __init__(self, api_endpoint: str, api_key: str, model: str):
        self.llm_api = LLMApi(api_endpoint=api_endpoint, api_key=api_key)
        self.refiner = PromptRefiner()
        # ...
```

**Benefits:**
- Easy testing with mocked dependencies
- Flexible configuration per workflow instance
- Clear separation of concerns

### Layered Architecture

Follow the strict four-layer architecture:
1. **CLI Layer**: User-facing commands and interfaces
2. **Workflow Layer**: Multi-stage orchestration logic
3. **Utility Layer**: Reusable helper functions
4. **API Layer**: LLM interaction abstraction

**Do not bypass layers** (e.g., CLI should not directly call API layer without going through workflows).

### Single Responsibility Principle

Each class and function should have one clear purpose:

```python
# Good: Focused responsibility
class PromptRefiner:
    """Handles prompt optimization and text cleaning."""
    pass

class FileHelper:
    """Centralized file system operations."""
    pass

# Avoid: Multiple responsibilities in one class
class ComplexProcessor:  # Bad: handles files, prompts, AND LLM calls
    pass
```

### Patterns to Avoid

- **Global state**: Use dependency injection instead of module-level globals
- **Deep inheritance hierarchies**: Prefer composition over inheritance
- **God objects**: Classes with excessive methods and responsibilities
- **Magic numbers**: Extract constants with descriptive names

---

## Testing Conventions

### Test Structure

```python
import pytest
from unittest.mock import Mock, patch


class TestLLMApi:
    """Tests for LLMApi class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.api = LLMApi(api_endpoint="http://test.local", api_key="test-key")
        
    @patch('sokrates.llm_api.OpenAI')
    def test_init_with_custom_values(self, mock_openai):
        """Test initialization with custom endpoint and key."""
        # Test implementation here
        pass
```

### Testing Principles

- **Unit tests** must mock external dependencies (`@patch`, `Mock`)
- **Integration tests** go in separate `integration_tests/` directory
- **Test method names**: `test_<what_is_tested>_<scenario>` pattern
- Use `pytest` assertions, not `unittest` assert methods

---

## Git and Version Control Conventions

### Commit Messages

Follow conventional commit format:

```
feat: add code review workflow for security analysis
fix: handle missing config file gracefully
docs: update API documentation with examples
refactor: extract file operations into FileHelper class
test: add unit tests for prompt refinement
chore: update dependencies to latest versions
```

### Branch Naming

- **Feature branches**: `feature/description` (e.g., `feature/code-analyzer`)
- **Bug fixes**: `fix/description` (e.g., `fix/missing-config-error`)
- **Chores**: `chore/description` (e.g., `chore/update-readme`)

---

*This conventions document was generated as part of the Sokrates project specification process.*
