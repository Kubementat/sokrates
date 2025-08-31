# Project structure
- README.md - general information about the project
- pyproject.toml - project configuration, dependencies and command listing
- docs/ - this directory contains documentation, feature planning and design
- src/sokrates - this directory contains all source code files
    - src/sokrates/cli - contains all cli command scripts
    - src/sokrates/coding - coding tools and coding workflow related code
    - src/sokrates/prompts - prompt templates for the automated workflows
    - src/sokrates/task_queue - task queue feature code including the task queue daemon (see sokrates-daemon command)
    - src/sokrates/workflows - workflow classes that implement the automated workflows
- tests/ - the pytest
- test_all_commands.py - a script for running the library's commands locally for testing

# Project Tools
- The project uses `uv` for managing and running python code
- All unit and integration tests are using the `pytest` library


## `uv` execution
General: uv run <COMMAND>

Examples:

```bash
uv run python -m pytest tests/
uv run sokrates-list-models
```

## Testing instructions
- For running the unit and integration tests run: `uv run python -m pytest tests/`
- For running the cli tool execution test run: `uv run test_all_commands.py`

# Rules
- ALWAYS use the `uv run` prefix for running any python scripts

# Project Summary
The sokrates project is a comprehensive framework for Large Language Model (LLM) interactions that provides advanced tools for prompt engineering, task management, idea generation, and Python coding assistance. It's designed to be modular, extensible, and production-ready.

## Key Components
1. **CLI Interface** - Contains all command-line tools organized by functionality:
   - Core LLM operations (list models, send prompts, chat)
   - Task management (breakdown tasks, execute tasks, task queue)
   - Idea generation and content creation
   - Benchmarking and analysis tools
   - Python coding tools (summarize, review, generate tests)

2. **Workflows** - Implements multi-stage processes:
   - Idea generation workflows
   - Refinement workflows
   - Sequential task execution
   - Benchmarking workflows

3. **Task Queue System** - Background processing with persistence:
   - Database management (SQLite)
   - Task processor and manager
   - Error handling and status tracking
   - Daemon for background processing

4. **Coding Tools** - Python-specific development assistance:
   - Code review workflows
   - Python analyzer
   - Test generator

5. **Prompt Engineering** - Prompt templates and refinement tools:
   - Multiple prompt refinement templates
   - Coding-specific prompts
   - Context management prompts

## Main Features and Capabilities
- Advanced prompt refinement with context awareness
- Streaming responses with performance metrics
- Multi-model support (OpenAI-compatible endpoints)
- Flexible context loading from files, directories, or text
- Intelligent response processing and formatting
- Background task processing with SQLite persistence
- Sequential task automation
- AI-powered task decomposition
- Priority queue system with status tracking
- Comprehensive error recovery and logging
- Voice-enabled chat with speech-to-text and text-to-speech capabilities
- Rich command-line interface with colorized output
- Automatic conversation logging
- Dynamic context switching during conversations
- Real-time CPU, memory, and resource usage tracking
- Performance metrics (token generation speed, response times)
- Comprehensive model benchmarking tools
- Structured logging infrastructure
- Modular architecture with clean separation of concerns
- Flexible environment-based configuration management
- Comprehensive file handling utilities
- Integrated pytest testing framework
- Extensive inline documentation and examples
- Idea generation with topic categorization
- Content creation (mantra generation, web content fetching, document merging)
- Python development assistance (code summarization, review, test generation)
- Model performance benchmarking and reporting

The project provides 15+ specialized CLI commands organized by functionality, making it a comprehensive toolkit for working efficiently with LLMs while maintaining production-ready standards and extensibility.