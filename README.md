# sokrates

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Version: 0.15.0](https://img.shields.io/badge/version-0.15.0-green)](https://github.com/Kubementat/sokrates)

A comprehensive framework for Large Language Model (LLM) interactions, featuring advanced prompt refinement, system monitoring, extensive CLI tools, and a robust task queue system. Designed to facilitate working with LLMs through modular components, well-documented APIs, and production-ready utilities.

[sokrates @PyPi](https://pypi.org/project/sokrates)

## Table of Contents
- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Command Structure](#basic-command-structure)
  - [Task Queuing System](#task-queuing-system)
  - [Daemon & File Watcher](#daemon--file-watcher)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Changelog](#changelog)

## Description

`sokrates` is a comprehensive framework for working with Large Language Models (LLMs). It provides a complete toolkit for developers and researchers to interact with LLMs efficiently and effectively.

### Core Capabilities:

- **Advanced Prompt Engineering**: Sophisticated prompt refinement tools that optimize LLM input/output for better performance
- **Voice-Enabled Chat**: Interactive command-line chat interface with optional voice input/output using OpenAI Whisper
- **Task Queue System**: Robust background task processing with persistence, error handling, and retry mechanisms
- **Task File Watcher**: Watcher checks for new file creations in a given directory and executes the task prompts within the files in the background
- **Multi-stage Workflows**: Complex task breakdown, idea generation, and sequential task execution
- **Python coding tools**: A set of useful tools for python coding
  - generate code reviews
  - generate test cases
  - summarize functionality
- **Comprehensive CLI Tools**: A unified command-line interface with multiple subcommands for LLM interaction, task management, code analysis, and content generation

### Key Features:

- **Modular Architecture**: Easily extensible components with clean separation of concerns
- **OpenAI-Compatible API**: Works with any OpenAI-compatible endpoint (LocalAI, Ollama, LM Studio, etc.)
- **Configuration Management**: Flexible configuration system with environment variable support
- **Output Processing**: Advanced text cleaning and formatting utilities for LLM-generated content
- **Performance Analytics**: Detailed timing metrics and token generation statistics
- **File Management**: Comprehensive file handling for context loading and result storage
- **CLI Tools**: For interacting with LLMs (for details: see [Usage](#usage))

## MCP available
There's the [sokrates-mcp server](https://github.com/Kubementat/sokrates-mcp) available for integrating sokrates tools via MCP.

## Installation

### Prerequisites

- Python 3.9 or higher
- Optional: FFmpeg (for voice features)
- Optional: Whisper-cpp (for enhanced voice processing)

### Install Prerequisites for Voice Features (Optional)

```bash
# On macOS
brew install ffmpeg
brew install whisper-cpp
brew install espeak-ng

# On Ubuntu/Debian
sudo apt-get install ffmpeg libportaudio2 portaudio19-dev espeak-ng
```

### Install from PyPI

```bash
pip install sokrates

# or using uv (recommended)
## basic version: 
uv pip install sokrates

## voice enabled version
uv pip install sokrates[voice]

# Test the installation (this expects you to have an OpenAI compatbile endpoint running on localhost:1234/v1 , e.g. via LM Studio or ollama)
sokrates list-models --api-endpoint http://localhost:1234/v1
```

### Install for Development

```bash
git clone https://github.com/Kubementat/sokrates.git
cd sokrates
uv sync # for basic version
uv sync --all-extras # for voice support enabled version
```

### Build the Library

To build a distributable package using `uv`:

```bash
# Basic version (without voice features)
uv build

# Build with all optional dependencies (voice support)
uv pip install -e ".[voice]"
uv build
```

This creates wheel and source distributions in the `dist/` directory. Verify with:

```bash
ls -la dist/
# Should show sokrates-$VERSION-py3-none-any.whl and similar files
```

### Dependencies

For a list of all dependencies view the [pyproject.toml](pyproject.toml) file.

## Configuration

You can configure the library via a yml configuration file in $HOME/.sokrates/config.yml

```
# Copy
cp config.yml.example $HOME/.sokrates/config.yml

# adjust to your needs
vim $HOME/.sokrates/config.yml
```

## Usage

### Basic Command Structure

The sokrates CLI provides a comprehensive set of commands for working with LLMs, managing tasks, analyzing code, and generating content. All commands follow a consistent structure:

```bash
sokrates <command> --option1 value1 --option2 value2
```

You can always display the help for any command via:

```bash
sokrates <command> --help
```

To list all available commands, run:

```bash
sokrates --help
```

### Daemon & File Watcher

The sokrates daemon includes a background file processor that monitors specified directories for new files and automatically processes them through the LLM refinement pipeline. This feature allows you to submit prompts by simply dropping text or markdown files into designated directories.

#### How It Works

1. The daemon starts a file watcher that monitors configured directories for new files
2. When a new file is detected, it's automatically processed through the LLM refinement pipeline
3. The file content is used as input to generate a refined prompt (if enabled via: refinement: true)
4. The refined prompt is executed via the configured LLM API
5. Results are saved to an output directory with timestamped filenames

#### Configuration

File watcher functionality is controlled through the configuration file (`$HOME/.sokrates/config.yml`):

```yaml
daemon:
  file_watcher:
    enabled: true  # Set to false to disable file watching
    watched_directories:
      - /path/to/watched/directory  # Add directories to monitor
    file_extensions:
      - ".txt"
      - ".md"
```

#### File Format and Metadata

Files processed by the daemon should contain your prompt content. You can also include YAML frontmatter to customize processing behavior:

```markdown
---
provider: local  # Use specific provider from config
model: qwen3-4b-instruct-2507-mlx  # Override default model
temperature: 0.7  # Set temperature for this prompt
refinement: true  # Enable or disable prompt refinement (default: false)
---

Your prompt content goes here...
```

#### Usage

To use this feature:

1. Configure the file watcher in your config.yml as shown above
2. Start the daemon: `sokrates-daemon start`
3. Drop text or markdown files into the configured watched directories
4. The daemon will automatically process each file and save results to the output directory

#### Output

Processed results are saved in the `$HOME/.sokrates/tasks/results` directory with timestamped filenames:

```
$HOME/.sokrates/tasks/results/
├── 20250929_143022_my_prompt_processed.md
└── 20250929_143105_another_request_processed.md
```

Each output file contains:
- Original file information
- The original content
- The refined prompt (if refinement was enabled)
- The execution result from the LLM
- Processing duration and error information (if any)

#### File Cleanup

After successful processing, the original input files are automatically deleted to prevent reprocessing.

#### Logs
The daemon writes logs to `$HOME/.sokrates/logs/daemon.log` .
Watch the log stream via:
```bash
tail -f $HOME/.sokrates/logs/daemon.log
```

### Example Usage

#### Basic LLM Operations

```bash
# List available models
sokrates-list-models --api-endpoint http://localhost:1234/v1

# Send a simple prompt
sokrates-send-prompt --model qwen3-4b-instruct-2507-mlx --prompt "Explain quantum computing in simple terms"

# Interactive chat with voice support
sokrates-chat --model qwen3-4b-instruct-2507-mlx --voice  # Enable voice mode

# Refine a prompt for better performance
sokrates-refine-prompt --prompt "Write a story about a robot" --model qwen3-4b-instruct-2507-mlx
```

#### Task Management

```bash
# Break down a complex project into tasks
sokrates-breakdown-task --task "Build a web application for task management" --output project-tasks.json

# Execute the generated tasks sequentially
sokrates-execute-tasks --task-file project-tasks.json --output-dir ./results

# Add a task to the background queue
sokrates-task-add tasks/feature_request.json --priority high

# Start the task queue daemon
sokrates-daemon start

# Check task status
sokrates-task-status --task-id abc123 --verbose

# List all pending tasks
sokrates-task-list --status pending --priority high
```

#### Idea Generation & Content Creation

```bash
# Generate creative ideas with topic categorization
sokrates-idea-generator --topic "AI in healthcare" --output-dir ./healthcare-ideas --idea-count 5

# Generate mantras for motivation
sokrates-generate-mantra -o my_mantra.md

# Convert web content to markdown
sokrates-fetch-to-md --url "https://example.com/article" --output article.md

# Merge multiple documents or ideas
sokrates-merge-ideas --source-documents 'docs/idea1.md,docs/idea2.md' --output-file merged-ideas.md
```

#### Python coding tools
```bash
# Analyze a directory with a code base and write the result to docs/code_analysis.md
sokrates-code-analyze --source-directory /dir/to/my_git_repo --output /dir/to/my_git_repo/docs/code_analysis.md

# Summarize python source classes and functions in the `src` directory
sokrates-code-summarize --source-directory src/ --output docs/code_summary.md

# Perform a code review for a list of code files or a directory
sokrates-code-review --files src/sokrates/config.py --verbose -o docs/code_reviews
```

## Features

### 🚀 Core LLM Capabilities
- **Advanced Prompt Refinement**: Multi-stage prompt optimization with context awareness
- **Streaming Responses**: Real-time token streaming with performance metrics
- **Multi-model Support**: Compatible with any OpenAI-compatible LLM endpoint
- **Context Management**: Flexible context loading from files, directories, or text
- **Response Processing**: Intelligent cleaning and formatting of LLM outputs

### 🎯 Task Management & Workflows
- **Task Queue System**: Background task processing with SQLite persistence
- **File Watcher**: Automatic directory monitoring with file content processing via LLM refinement
- **Sequential Task Execution**: Complex multi-step task automation
- **Task Breakdown**: AI-powered task decomposition into manageable sub-tasks
- **Priority Queue**: Task prioritization and status tracking
- **Error Handling**: Comprehensive error recovery and logging

### 💬 Interactive Features
- **Voice-Enabled Chat**: Speech-to-text and text-to-speech capabilities using Whisper
- **Interactive CLI**: Rich command-line interface with colorized output
- **Conversation Logging**: Automatic chat history logging with timestamps
- **Context Switching**: Dynamic context addition during conversations

### 🔧 Developer Tools
- **Modular Architecture**: Clean, extensible component design
- **Configuration Management**: Flexible environment-based configuration
- **File Management**: Comprehensive file handling utilities
- **Testing Framework**: Integrated pytest with comprehensive test coverage
- **Documentation**: Extensive inline documentation and examples

### 🎨 User Experience
- **Rich CLI Output**: Colorized, formatted output with progress indicators
- **Help System**: Comprehensive help and usage instructions for all commands
- **Error Handling**: User-friendly error messages and recovery suggestions
- **Cross-platform**: Works on macOS, Linux, and Windows

## Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository** and create a new branch for your feature
2. **Make your changes** with appropriate tests and documentation
3. **Run the test suite** to ensure everything works correctly
4. **Submit a pull request** with a clear description of your changes

### Development Setup

```bash
git clone https://github.com/Kubementat/sokrates.git
cd sokrates
uv sync --all-extras
uv pip install -e .
source .venv/bin/activate
```

### Run the testsuite
For the testsuite we expect a locally running LM Studio instance with the default model [qwen3-4b-instruct-2507-mlx](https://huggingface.co/lmstudio-community/Qwen3-4B-Instruct-2507-MLX-4bit) available and ready for execution. You can also specify another testing model in [conftest.py](tests/conftest.py).
For details for setting up LM Studio visit [their documentation](https://lmstudio.ai/docs/app).

```bash
# run all unit tests
uv run python -m pytest tests

# run only unit tests (without LLM interactions)
uv run python -m pytest tests --ignore=tests/integration_tests

# run the integartion pytest testsuite
uv run python -m pytest tests/integration_tests

# run integration tests using the commands
uv run test_all_commands.py
# for options check
uv run test_all_commands.py --help
```

### Guidelines

- Follow the existing code style and conventions
- Add tests for new functionality
- Update documentation for significant changes
- Ensure all existing tests pass

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contact

**Julian Weber** - Creator and Maintainer

- 📧 Email: [julianweberdev@gmail.com](mailto:julianweberdev@gmail.com)
- 🐙 GitHub: [@julweber](https://github.com/julweber)
- 💼 LinkedIn: [Julian Weber](https://www.linkedin.com/in/julianweberdev/)

**Project Links:**
- 🏠 Homepage: https://github.com/Kubementat/sokrates
- 📚 Documentation: See [docs/](docs/) directory for detailed documentation
- 🐛 Issues: [GitHub Issues](https://github.com/Kubementat/sokrates/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/Kubementat/sokrates/discussions)

## Changelog

View our [CHANGELOG.md](CHANGELOG.md) for a detailed changelog.
