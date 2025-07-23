# sokrates

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Version: 0.2.9](https://img.shields.io/badge/Version-0.2.9-brightgreen.svg)](https://github.com/Kubementat/sokrates)

A collection of tools for LLM interactions and system monitoring, designed to facilitate working with Large Language Models (LLMs) through modular components, well-documented APIs, and production-ready utilities.

## Table of Contents
- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
  - [Available Commands](#available-commands)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Changelog](#changelog)

## Description

`sokrates` is a comprehensive framework for working with Large Language Models (LLMs). It provides:

- Advanced prompt refinement tools
- System monitoring for resource tracking during LLM operations
- An extensive CLI interface for rapid experimentation
- Modular components and well-documented APIs

The project includes utilities for:
- Managing configuration settings
- Interacting with OpenAI-compatible LLM APIs
- Processing and cleaning LLM-generated text
- Monitoring system resources in real-time
- Executing complex workflows for idea generation and prompt refinement

## Installation

Prerequisites: Python 3.9 or higher

```bash
git clone https://github.com/Kubementat/sokrates.git
cd sokrates
uv sync
```

## Usage

### Basic Command Structure

Most commands follow this structure:
```bash
command --option1 value1 --option2 value2
```

You can always display the help via:
```
command --help

e.g.

uv run list-models --help
```

### Available Commands

- `benchmark-model`: Benchmark LLM models
- `benchmark-results-merger`: Merge benchmark results
- `benchmark-results-to-markdown`: Convert benchmark results to markdown
- `fetch-to-md`: Fetch content and convert to markdown
- `generate-mantra`: Generate mantras or affirmations
- `list-models`: List available LLM models
- `idea-generator`: Generate ideas using a multi-stage workflow
- `refine-and-send-prompt`: Refine and send prompts to a LLM
- `refine-prompt`: Refine prompts for better LLM performance
- `breakdown-task`: Break down complex tasks into manageable steps
- `send-prompt`: Send a prompt to a LLM API
- `llmchat`: Chat with LLMs via the command line

### Example Usage

```bash
# Getting help for a command and usage instructions
uv run refine-prompt --help

# List available models
uv run list-models --api-endpoint http://localhost:1234/v1

# Generate ideas
uv run idea-generator --output-directory tmp/ideas --verbose

# Benchmark a model
uv run benchmark-model --model qwen/qwen3-8b --iterations 5
```

## Features

- **Prompt Refinement**: Optimize LLM input/output with advanced refinement tools
- **System Monitoring**: Real-time tracking of resource usage during LLM operations
- **CLI Interface**: Extensive command-line tools for rapid experimentation
- **Modular Architecture**: Easily extendable and customizable components
- **Testing Infrastructure**: Built-in test framework with pytest integration

## Contributing

1. Fork the repository and create a new branch
2. Make your changes and add tests if necessary
3. Submit a pull request with a clear description of your changes

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contact

- [julianweberdev@gmail.com](mailto:julianweberdev@gmail.com)
- GitHub: [@julweber](https://github.com/julweber)
- Linked.in : [Julian Weber](https://www.linkedin.com/in/julianweberdev/)

## Changelog

View our [CHANGELOG.md](CHANGELOG.md) for a detailed changelog.