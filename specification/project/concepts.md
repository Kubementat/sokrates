# Domain Concepts

This document defines the key terminology, domain entities, and conceptual frameworks used throughout Sokrates. Understanding these concepts is essential for effectively using the framework.

---

## Core Domain Entities

### Task

A discrete unit of work to be executed by the LLM system. Tasks can be:

- **Synchronous**: Executed immediately via CLI commands
- **Background**: Queued for later processing with priority levels (low, normal, high)

Each task has associated metadata including description, file path, status tracking, and result storage.

### Workflow

A multi-stage orchestration pattern that coordinates complex LLM interactions across several phases. Examples include:

- **RefinementWorkflow**: Multi-stage prompt optimization before execution
- **IdeaGenerationWorkflow**: Automated topic generation and content creation
- **CodeReviewWorkflow**: Systematic analysis of Python codebases

Workflows chain together multiple operations (prompt generation, refinement, execution) with intermediate result handling.

### Prompt

A text input sent to an LLM for processing. In Sokrates, prompts go through a lifecycle:

1. **Raw Input**: User-provided initial prompt
2. **Refined**: Optimized version after applying refinement rules
3. **Executed**: Final form sent to the model

Prompts can include context from files and support YAML frontmatter for configuration.

### Model

The specific Large Language Model instance used for generation (e.g., `qwen3-4b-instruct`, `llama-3`). Each model has associated properties:

- **Capabilities**: Supported features (streaming, function calling)
- **Tokens per second**: Performance characteristics
- **Context window**: Maximum input/output token capacity

### Provider

A configuration profile for an LLM endpoint. Providers abstract the underlying service:

- **Name**: Identifier (e.g., `local`, `openai`)
- **Type**: API format (currently OpenAI-compatible)
- **Endpoint URL**: REST API location
- **Default model and temperature**: Configuration defaults

Sokrates supports any OpenAI-compatible endpoint including LocalAI, Ollama, LM Studio, and custom deployments.

### Refinement

The process of optimizing prompts before or after LLM interaction:

- **Pre-execution refinement**: Clean and optimize user prompts for better results
- **Post-processing**: Remove artifacts from LLM responses (thinking tags, prefixes, formatting issues)

Refinement ensures consistent markdown output and removes common noise patterns.

### Execution

The actual invocation of an LLM via the configured API endpoint. Executions track:

- **Time to first token**: Latency measurement
- **Tokens per second**: Throughput metric
- **Total duration**: End-to-end timing

---

## Key Abstractions

### Layered Architecture

Sokrates follows a strict separation of concerns across four layers:

```
┌─────────────────────────────────────┐
│          CLI Layer                  │  ← User-facing commands and interfaces
├─────────────────────────────────────┤
│       Workflow Layer                │  ← Multi-stage orchestration logic
├─────────────────────────────────────┤
│        Utility Layer                │  ← Reusable helper functions
├─────────────────────────────────────┤
│          API Layer                  │  ← LLM interaction abstraction
└─────────────────────────────────────┘
```

This enables:
- Easy testing with mocked dependencies
- Flexible configuration per component
- Clear extension points for new features

### Synchronous vs Background Processing

Sokrates supports two execution modes:

| Mode | Characteristics | Use Cases |
|------|----------------|-----------|
| **Synchronous** | Immediate execution, blocks until completion | Interactive chat, quick prompts |
| **Background** | Queued processing, non-blocking | Long-running tasks, file monitoring |

The task queue system enables background processing with SQLite persistence and retry mechanisms.

### Provider Abstraction

The provider concept allows users to switch between different LLM endpoints without changing code:

```python
# Local endpoint (Ollama/LM Studio)
provider = "local"
endpoint = "http://localhost:1234/v1"

# Remote endpoint (OpenAI-compatible service)
provider = "custom"
endpoint = "https://api.example.com/v1"
```

All LLM interactions route through the `LLMApi` interface, which handles provider-specific details.

---

## Configuration Concepts

### Home Path

The root directory for Sokrates configuration and data:

- **Default**: `$HOME/.sokrates`
- **Override**: Environment variable `SOKRATES_HOME_PATH`

Contains subdirectories for config, database, logs, and task files.

### Daemon Process

A long-running background service that processes queued tasks at configurable intervals. Features include:

- Signal handling for graceful shutdown
- Automatic status updates on termination
- Comprehensive logging to daemon log file
- File watcher for automatic processing of new files

---

*This concepts document was generated as part of the Sokrates project specification process.*
