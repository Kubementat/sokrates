# LLM Context Documentation for sokrates

This document provides comprehensive context about the sokrates project to help Large Language Models better understand the codebase, its architecture, and usage patterns.

## Project Overview

**sokrates** is a comprehensive Python framework for Large Language Model (LLM) interactions, designed to facilitate working with LLMs through modular components, well-documented APIs, and production-ready utilities.

### Key Information
- **Version**: 0.4.2
- **License**: MIT
- **Python Version**: 3.9+
- **Main Dependencies**: openai, psutil, requests, click, tabulate, colorama, markdownify, dotenv, openai-whisper, pyaudio
- **Repository**: https://github.com/Kubementat/sokrates

## Architecture Overview

### Core Modules

#### 1. **LLM API Interface** (`src/sokrates/llm_api.py`)
- **Purpose**: Primary interface for OpenAI-compatible LLM interactions
- **Key Features**:
  - Model listing and discovery
  - Streaming responses with performance metrics
  - Context-aware prompt generation
  - Chat completion support
  - Error handling and retry logic
- **Main Class**: `LLMApi`
- **Key Methods**:
  - `list_models()`: Returns available model IDs
  - `send()`: Sends prompts to LLM with context support
  - `chat_completion()`: Handles conversation history
  - `combine_context()`: Merges multiple context sources

#### 2. **Configuration Management** (`src/sokrates/config.py`)
- **Purpose**: Centralized configuration management
- **Key Features**:
  - Environment variable loading
  - Default value management
  - Directory structure creation
  - Singleton pattern implementation
- **Main Class**: `Config`
- **Key Attributes**:
  - `DEFAULT_API_ENDPOINT`: "http://localhost:1234/v1"
  - `DEFAULT_API_KEY`: "notrequired"
  - `DEFAULT_MODEL`: "qwen/qwen3-8b"
  - `DEFAULT_MODEL_TEMPERATURE`: 0.7

#### 3. **Prompt Refinement** (`src/sokrates/prompt_refiner.py`)
- **Purpose**: Advanced text processing and LLM output cleaning
- **Key Features**:
  - Meta-element removal (thinking blocks, reasoning blocks)
  - Markdown formatting and conversion
  - Response cleaning and sanitization
  - JSON response processing
- **Main Class**: `PromptRefiner`
- **Key Methods**:
  - `clean_response()`: Removes unwanted elements from LLM output
  - `format_as_markdown()`: Ensures proper Markdown formatting
  - `clean_json_response()`: Processes JSON-formatted responses

#### 4. **Task Queue System** (`src/sokrates/task_queue/`)
- **Purpose**: Background task processing with persistence
- **Key Components**:
  - `database.py`: SQLite database operations
  - `manager.py`: High-level task management interface
  - `processor.py`: Task execution logic
  - `daemon.py`: Background process management
  - `status_tracker.py`: Task status monitoring
  - `error_handler.py`: Error recovery and logging
- **Main Class**: `TaskQueueManager`
- **Features**:
  - Task persistence and recovery
  - Priority-based processing
  - Error handling and retries
  - Status tracking and logging

#### 5. **Sequential Task Executor** (`src/sokrates/sequential_task_executor.py`)
- **Purpose**: Execute complex multi-step workflows
- **Key Features**:
  - JSON-based task definition
  - Sequential task execution
  - Result aggregation and storage
  - Progress tracking
- **Main Class**: `SequentialTaskExecutor`
- **Workflow**:
  1. Load tasks from JSON file
  2. Process each task through refinement workflow
  3. Execute refined prompts
  4. Save results to output directory

#### 6. **Idea Generation Workflow** (`src/sokrates/idea_generation_workflow.py`)
- **Purpose**: Multi-stage idea generation and refinement
- **Key Features**:
  - Topic generation with categorization
  - Prompt generation from templates
  - Multi-stage refinement process
  - Random category selection
- **Main Class**: `IdeaGenerationWorkflow`
- **Process Flow**:
  1. Generate or load topic
  2. Create execution prompts
  3. Refine each prompt
  4. Execute refined prompts
  5. Save results

#### 7. **CLI Interface** (`src/sokrates/cli/`)
- **Purpose**: Command-line interface for all functionality
- **Structure**:
  - Root CLI commands in `src/sokrates/cli/`
  - Task queue commands in `src/sokrates/cli/task_queue/`
- **Key Commands**:
  - `sokrates-chat`: Interactive chat interface
  - `sokrates-list-models`: Model discovery
  - `sokrates-breakdown-task`: Task decomposition
  - `sokrates-execute-tasks`: Sequential execution
  - `sokrates-daemon`: Task queue management

#### 8. **System Monitoring** (`src/sokrates/system_monitor.py`)
- **Purpose**: Real-time resource usage tracking
- **Key Features**:
  - CPU and memory monitoring
  - Performance metrics collection
  - Resource usage reporting
- **Main Class**: `SystemMonitor`

#### 9. **Voice Helper** (`src/sokrates/voice_helper.py`)
- **Purpose**: Speech-to-text and text-to-speech capabilities
- **Key Features**:
  - Whisper integration for speech recognition
  - Audio input/output handling
  - Voice chat mode support

#### 10. **File Utilities** (`src/sokrates/file_helper.py`)
- **Purpose**: Comprehensive file handling operations
- **Key Features**:
  - File reading and writing
  - JSON processing
  - Directory management
  - File name cleaning and validation

#### 11. **Output Management** (`src/sokrates/output_printer.py`)
- **Purpose**: Formatted console output
- **Key Features**:
  - Colorized output
  - Progress indicators
  - Structured logging
  - Error formatting

## Configuration System

### Environment Variables
The project uses environment variables for configuration:

```bash
# API Configuration
SOKRATES_API_ENDPOINT=http://localhost:1234/v1
SOKRATES_API_KEY=notrequired
SOKRATES_DEFAULT_MODEL=qwen/qwen3-8b
SOKRATES_DEFAULT_MODEL_TEMPERATURE=0.7

# File Paths
SOKRATES_CONFIG_FILEPATH=$HOME/.sokrates/.env
SOKRATES_DATABASE_PATH=$HOME/.sokrates/sokrates_database.sqlite
SOKRATES_TASK_QUEUE_DAEMON_LOGFILE_PATH=$HOME/.sokrates/logs/daemon.log
```

### Directory Structure
```
$HOME/.sokrates/
├── .env                    # Configuration file
├── sokrates_database.sqlite # Task queue database
├── logs/                   # Log files
│   └── daemon.log
├── tasks/                  # Task execution results
│   └── results/
└── chats/                  # Chat logs
```

## CLI Command Reference

### Core LLM Commands
```bash
sokrates-list-models --api-endpoint ENDPOINT
sokrates-send-prompt --model MODEL --prompt "PROMPT"
sokrates-chat --model MODEL --voice --context-files FILE.md
sokrates-refine-prompt --prompt "PROMPT" --model MODEL
```

### Task Management Commands
```bash
sokrates-breakdown-task --task "DESCRIPTION" --output tasks.json
sokrates-execute-tasks --task-file tasks.json --output-dir ./results
sokrates-task-add tasks/feature.json --priority high
sokrates-daemon start|stop|restart|status
```

### Content Generation Commands
```bash
sokrates-idea-generator --topic "TOPIC" --output-dir ./ideas --idea-count 5
sokrates-generate-mantra --count 3 --theme "productivity"
sokrates-fetch-to-md --url "URL" --output article.md
```

### Benchmarking Commands
```bash
sokrates-benchmark-model --model MODEL --iterations 10
sokrates-benchmark-results-to-markdown --input results.json --output report.md
```

## Data Structures

### Task Queue Format
```json
{
  "task_id": "uuid",
  "description": "Task description",
  "file_path": "/path/to/task.json",
  "priority": "high|normal|low",
  "status": "pending|running|completed|failed",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "result": "execution result",
  "error": "error message"
}
```

### Task Breakdown Format
```json
{
  "task": "Main task description",
  "subtasks": [
    {
      "id": 1,
      "description": "Sub-task description",
      "complexity": "low|medium|high"
    }
  ]
}
```

### Idea Generation Format
```json
{
  "prompts": [
    {
      "title": "Prompt title",
      "description": "Prompt description",
      "category": "Topic category"
    }
  ]
}
```

## Error Handling Patterns

### API Error Handling
```python
try:
    result = llm_api.send(prompt, model=model)
except Exception as e:
    OutputPrinter.print_error(f"API Error: {e}")
    # Handle error appropriately
```

### File Operation Error Handling
```python
try:
    content = FileHelper.read_file(filepath, verbose=True)
except FileNotFoundError:
    OutputPrinter.print_error(f"File not found: {filepath}")
except Exception as e:
    OutputPrinter.print_error(f"File error: {e}")
```

### Task Queue Error Handling
```python
try:
    task_manager.add_task_from_file(task_file)
except ValueError as e:
    OutputPrinter.print_error(f"Task validation error: {e}")
except Exception as e:
    OutputPrinter.print_error(f"Task queue error: {e}")
```

## Performance Considerations

### LLM API Optimization
- Use streaming responses for better user experience
- Implement context caching for repeated operations
- Monitor token usage and response times
- Handle rate limiting gracefully

### System Resource Management
- Monitor CPU and memory usage during LLM operations
- Implement proper cleanup of resources
- Use connection pooling for API calls
- Cache frequently accessed data

### File I/O Optimization
- Use buffered reading for large files
- Implement proper file handle management
- Use asynchronous operations where appropriate
- Implement proper error handling for file operations

## Testing Strategy

### Unit Tests
- Located in `tests/` directory
- Use pytest framework
- Cover core functionality and edge cases
- Mock external dependencies (API calls, file operations)

### Integration Tests
- Test CLI command functionality
- Verify task queue operations
- Test file handling and data processing
- Validate error handling scenarios

### Performance Tests
- Benchmark LLM API performance
- Test task queue scalability
- Monitor resource usage under load
- Validate response time requirements

## Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Implement comprehensive docstrings
- Use meaningful variable and function names

### Documentation
- Include inline comments for complex logic
- Update documentation when changing APIs
- Provide usage examples for new features
- Maintain CHANGELOG.md for version updates

### Version Control
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Follow conventional commit messages
- Maintain clear branch naming conventions
- Ensure all changes have appropriate tests

## Common Use Cases

### 1. Simple LLM Interaction
```python
from sokrates import LLMApi, Config

api = LLMApi(api_endpoint=Config().api_endpoint, api_key=Config().api_key)
response = api.send("Explain quantum computing", model="qwen/qwen3-8b")
```

### 2. Task Breakdown and Execution
```python
from sokrates import SequentialTaskExecutor

executor = SequentialTaskExecutor()
results = executor.execute_tasks_from_file("project_tasks.json")
```

### 3. Idea Generation Workflow
```python
from sokrates import IdeaGenerationWorkflow

workflow = IdeaGenerationWorkflow(
    api_endpoint=Config().api_endpoint,
    api_key=Config().api_key,
    topic="AI in healthcare",
    output_directory="./ideas"
)
ideas = workflow.run()
```

### 4. Task Queue Management
```python
from sokrates.task_queue import TaskQueueManager

with TaskQueueManager() as manager:
    task_id = manager.add_task_from_file("task.json", priority="high")
    tasks = manager.get_pending_tasks()
    manager.update_task_status(task_id, "completed", result="Task completed")
```

This documentation provides comprehensive context about the sokrates project, its architecture, and usage patterns to help LLMs better understand and work with the codebase effectively.