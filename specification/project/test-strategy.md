# Testing Strategy

This document defines the testing approach, frameworks, and practices for Sokrates. The goal is to ensure code quality, catch regressions early, and maintain confidence in the codebase through automated testing.

---

## Overview

Sokrates uses a multi-tiered testing strategy that separates tests by their dependencies and execution requirements. This allows developers to run quick unit tests during development while maintaining comprehensive integration tests for end-to-end validation.

---

## Test Categories

### Unit Tests

**Purpose**: Test individual components in isolation with mocked external dependencies.

**Characteristics:**
- Run quickly (milliseconds per test)
- Do not require network access or LLM endpoints
- Use mocks and fakes for all external dependencies
- Located in `tests/unit_tests/` directory

**Scope:**
- All public API methods
- Business logic and data transformations
- Error handling paths
- Configuration parsing and validation

**Example:**
```python
from unittest.mock import Mock, patch


class TestFileHelper:
    """Tests for FileHelper class."""
    
    def test_read_file_not_found(self):
        """Test handling of missing files."""
        helper = FileHelper()
        with pytest.raises(FileNotFoundError):
            helper.read_file(Path("/nonexistent/file.txt"))
```

### Integration Tests

**Purpose**: Test components interacting with real external systems.

**Characteristics:**
- Require local LLM endpoint (e.g., LM Studio, Ollama on `localhost:1234`)
- Run slower than unit tests (seconds per test)
- Validate end-to-end workflows
- Located in `tests/integration_tests/` directory

**Scope:**
- LLM API interactions with real endpoints
- CLI command execution and output formatting
- Task queue persistence and daemon behavior
- File watcher automatic processing

**Requirements:**
- Running LLM service on configured endpoint
- Default test model: `qwen3-4b-instruct-2507` (configurable in `conftest.py`)
- Network access if using remote endpoints

**Example:**
```python
class TestLLMApiIntegration:
    """Tests requiring LLM endpoint."""
    
    def test_list_models(self, llm_api):
        """Test model listing from actual endpoint."""
        models = llm_api.list_models()
        assert len(models) > 0
        
    def test_send_prompt_streaming(self, llm_api):
        """Test streaming response handling."""
        results = list(llm_api.stream_response("Hello", max_tokens=50))
        assert all(isinstance(r, dict) for r in results)
```

---

## Testing Frameworks and Tools

### Primary Framework: pytest

Sokrates uses `pytest` as the testing framework due to its:
- Expressive assertion style (no need for self.assertXxx methods)
- Rich plugin ecosystem
- Automatic test discovery via naming conventions
- Fixtures and parametrization support

**Configuration:** Defined in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
addopts = "-v --tb=short"
markers = [
    "integration: marks tests as requiring LLM endpoint",
    "slow: marks tests as slow-running",
]
```

### Essential Plugins

| Plugin | Purpose | Usage |
|--------|---------|-------|
| **pytest-mock** | Mocking and patching external dependencies | `@patch()`, `Mock()` objects |
| **pytest-cov** | Code coverage reporting | `--cov=src/sokrates --cov-report=term` |

### Optional Tools (Future Consideration)

- **hypothesis**: Property-based testing for edge case discovery
- **pytest-xdist**: Parallel test execution for faster CI runs
- **pytest-timeout**: Enforce maximum test duration

---

## Test Execution Commands

### Running All Tests

```bash
# Run all tests (excluding integration tests by default)
uv run python -m pytest tests --ignore=tests/integration_tests

# Run with coverage reporting
uv run python -m pytest --cov=src/sokrates --cov-report=term-missing tests/

# Run with verbose output and detailed traces
uv run python -m pytest -v tests/
```

### Running Integration Tests Only

```bash
# Run all integration tests (requires LLM endpoint)
uv run python -m pytest tests/integration_tests

# Run specific integration test file
uv run python -m pytest tests/integration_tests/test_llm_api.py
```

### Running Single Test

```bash
# Run a specific test function
uv run python -m pytest tests/unit_tests/test_file_helper.py::TestFileHelper::test_read_file_not_found

# Run with verbose output
uv run python -m pytest tests/unit_tests/test_file_helper.py::TestFileHelper::test_read_file_not_found -vvv
```

### Test Discovery Patterns

- **Files**: Must match `test_*.py` pattern
- **Classes**: Must start with `Test` (e.g., `TestLLMApi`)
- **Methods**: Must start with `test_` (e.g., `test_init_with_custom_values`)

---

## Test Organization

### Directory Structure

```
tests/
├── integration_tests/          # Tests requiring LLM endpoint or external systems
│   ├── test_llm_api.py
│   └── test_cli_commands.py
├── unit_tests/                 # Self-contained tests with mocks
│   ├── test_file_helper.py
│   ├── test_prompt_refiner.py
│   └── test_config.py
├── conftest.py                # Shared fixtures and configuration
└── fixtures/                  # Test data files (JSON, YAML, etc.)
    └── sample_configs.yaml
```

### Fixtures Directory

The `tests/fixtures/` directory contains reusable test data:
- Sample configuration files for testing parsing logic
- Mock LLM responses for API tests
- Sample code snippets for analysis workflows

---

## Best Practices

### Mocking External Dependencies

Always mock external systems in unit tests to ensure isolation and speed:

```python
from unittest.mock import Mock, patch


class TestRefinementWorkflow:
    """Tests for RefinementWorkflow."""
    
    @patch('sokrates.workflows.refinement_workflow.LLMApi')
    def test_refine_prompt_with_mocked_api(self, mock_llm_class):
        """Test prompt refinement with mocked LLM API."""
        mock_instance = Mock()
        mock_instance.send_message.return_value = "Refined: Your prompt"
        mock_llm_class.return_value = mock_instance
        
        workflow = RefinementWorkflow(
            api_endpoint="http://test.local",
            api_key="test-key",
            model="test-model"
        )
        
        result = workflow.refine("raw prompt")
        assert "Refined:" in result
```

### Test Method Naming Convention

Use descriptive names that communicate the test's purpose:

```python
# Good naming patterns
def test_init_with_custom_values():
    def test_read_file_not_found_raises_exception():
    def test_process_data_validates_input_format():
    
# Avoid vague names
def test1():  # ❌ What does it test?
def test_processing():  # ❌ Too broad
```

### Parameterized Tests

Use `@pytest.mark.parametrize` for testing multiple scenarios:

```python
@pytest.mark.parametrize(
    "input_value,expected_output",
    [
        ("valid_prompt", "refined: valid_prompt"),
        ("another_input", "refined: another_input"),
    ]
)
def test_refine_various_inputs(input_value, expected_output):
    """Test prompt refinement with various inputs."""
    result = workflow.refine(input_value)
    assert result == expected_output
```

### Error Handling Tests

Explicitly test error paths and exception handling:

```python
def test_invalid_temperature_raises_value_error():
    """Test that out-of-range temperature raises ValueError."""
    with pytest.raises(ValueError, match="Temperature must be between"):
        workflow.set_temperature(1.5)


@patch('sokrates.llm_api.OpenAI')
def test_network_failure_raises_connection_error(mock_openai):
    """Test handling of network failures during API calls."""
    mock_openai.side_effect = requests.ConnectionError("No internet")
    
    with pytest.raises(ConnectionError):
        llm_api.send_message("test prompt")
```

---

## Coverage Goals

While no minimum coverage threshold is enforced, the goal is to maintain comprehensive test coverage:

- **Core modules**: `llm_api.py`, `file_helper.py`, `config.py` should have high coverage (>90%)
- **CLI commands**: All public CLI commands should have at least one integration test
- **Workflows**: Business logic paths should be covered, including error scenarios
- **New features**: New code should include tests before merging

Use coverage reporting to identify gaps:

```bash
uv run python -m pytest --cov=src/sokrates --cov-report=html tests/
# Opens htmlcov/index.html with detailed coverage breakdown
```

---

## Continuous Integration Considerations

While no CI configuration is currently required, future CI integration should consider:

### Test Execution Strategy

1. **On Pull Request**: Run unit tests only (fast feedback)
2. **On Main Branch Merge**: Run all tests including integration (requires endpoint setup)
3. **Scheduled Runs**: Weekly full test suite to catch regressions

### Environment Setup for CI

```yaml
# Example GitHub Actions snippet
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.12'

- name: Install dependencies
  run: |
    uv sync --all-extras
    
- name: Run unit tests
  run: uv run python -m pytest tests --ignore=tests/integration_tests
  
- name: Start LM Studio (for integration tests)
  # Requires container or service setup
  
- name: Run integration tests
  run: uv run python -m pytest tests/integration_tests
```

---

## Test Maintenance Guidelines

### Updating Tests When Refactoring

When modifying code that has existing tests:
1. **Run affected tests first** to identify breakage
2. **Update test expectations** to match new behavior
3. **Add regression tests** for any bugs discovered during refactoring

### Deprecating Old Features

When removing functionality:
1. **Mark as deprecated** in code with warnings
2. **Keep integration tests** until deprecation period ends
3. **Remove unit test files** after full removal

---

*This testing strategy document was generated as part of the Sokrates project specification process.*
