# Technical Architecture

This document describes the high-level technical design of Sokrates, including technology choices, system structure, component interactions, and deployment considerations.

---

## Technology Stack

### Core Technologies

| Category          | Technology         | Purpose                                                          |
| -------------------| --------------------| ------------------------------------------------------------------|
| **Language**      | Python 3.9+        | Primary development language with full type hint support         |
| **CLI Framework** | Click              | Command-line interface definition and parsing                    |
| **LLM SDK**       | OpenAI             | Unified API for LLM interactions (supports compatible endpoints) |
| **Database ORM**  | Peewee [playhouse] | SQLite database operations with connection pooling               |
| **YAML Parsing**  | ruamel.yaml        | Configuration file handling with formatting preservation         |
| **File Watching** | watchdog           | Directory monitoring for automatic file processing               |

### Optional Dependencies (Voice Features)

| Technology | Purpose |
|------------|---------|
| **openai-whisper** | Speech-to-text conversion |
| **TTS** | Text-to-speech synthesis |

Voice features are opt-in and disabled by default.

---

## System Structure

### Monolithic Architecture

Sokrates follows a monolithic architecture with clear internal boundaries:

```
┌─────────────────────────────────────────────────────────────┐
│                        Sokrates CLI                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  cli/    │  │ coding/  │  │ task_    │  │workflows/ │   │
│  │ commands │  │ tools    │  │ queue/   │  │ pipelines │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │             │             │          │
│       └─────────────┴─────────────┴─────────────┘          │
│                            │                               │
│                    ┌───────▼────────┐                      │
│                    │    config.py   │                      │
│                    ├────────────────┤                      │
│                    │ file_helper.py │                      │
│                    ├────────────────┤                      │
│                    │ llm_api.py     │                      │
│                    ├────────────────┤                      │
│                    │ utils.py       │                      │
│                    └────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

**Key Characteristics:**
- Single executable (`sokrates`) with multiple subcommands
- All components built into one package (PyPI distribution)
- No microservices or external services required for core functionality
- Self-contained deployment suitable for local development

---

## Component Architecture

### Layered Design Pattern

Sokrates implements a strict four-layer architecture:

#### 1. CLI Layer (`cli/`)

**Responsibility**: User-facing commands and interfaces

**Key Components:**
- `colors.py`: ANSI color definitions for output formatting
- `helper.py`: CLI utility functions (argument parsing, validation)
- `output_printer.py`: Formatted tables and structured output
- Subdirectories: `coding/`, `task_queue/` for command organization

**Design Principles:**
- Thin layer that delegates to workflow or utility layers
- Input validation and error handling at boundaries
- Colorized console output via `Colors` class

#### 2. Workflow Layer (`workflows/`)

**Responsibility**: Multi-stage orchestration logic

**Key Workflows:**
- **RefinementWorkflow**: Prompt optimization pipeline
- **IdeaGenerationWorkflow**: Topic generation with categorization
- **CodeReviewWorkflow**: Automated code analysis (style, security, performance)
- **MergeIdeasWorkflow**: Document combination and synthesis
- **SequentialTaskExecutor**: Multi-step task orchestration

**Design Principles:**
- Composable stages with clear interfaces
- Dependency injection for testability
- State management across pipeline phases

#### 3. Utility Layer (`utils/`, `file_helper.py`, etc.)

**Responsibility**: Reusable helper functions and utilities

**Key Utilities:**
- **FileHelper**: Centralized file system operations (read, write, combine)
- **PromptRefiner**: Text cleaning and markdown formatting
- **SystemMonitor**: Resource usage tracking
- **LLMApi**: LLM interaction abstraction with metrics
- **VoiceHelper**: Speech-to-text integration

**Design Principles:**
- Single responsibility per module
- Comprehensive error handling with descriptive exceptions
- Logging at appropriate levels (DEBUG for detailed operations)

#### 4. API Layer (`llm_api.py`)

**Responsibility**: LLM interaction abstraction

**Key Features:**
- OpenAI SDK wrapper supporting any compatible endpoint
- Streaming response handling with real-time metrics
- Context management via message building
- Model listing and validation

**Metrics Tracked:**
- Time to first token (latency perception)
- Tokens per second (throughput)
- Total generation duration

---

## Data Flow

### Synchronous Command Execution

```
User Input → CLI Parser → Workflow/Utility → LLM API → Response → Formatted Output
     │           │            │              │            │             │
     └───────────┴────────────┴──────────────┴────────────┴─────────────┘
                    Request Cycle (1-3 seconds typical)
```

### Background Task Processing

```
Task Add → SQLite DB → Daemon Polls → Task Processor → LLM API → Result Saved
     │         │             │              │              │           │
     └─────────┴─────────────┴──────────────┴──────────────┴───────────┘
                        Queue Interval (default: 15 seconds)
```

### File Watcher Pipeline

```
New File Detected → Read Frontmatter → Parse Metadata → Refine Prompt → Execute → Save Results
     │                  │                │               │             │          │
     └──────────────────┴────────────────┴───────────────┴─────────────┴──────────┘
                              Automatic Processing (when enabled)
```

---

## Configuration System

### Configuration Hierarchy

1. **Environment Variable**: `SOKRATES_HOME_PATH` overrides default location
2. **User Config File**: `$HOME/.sokrates/config.yml` with provider definitions
3. **Command-Line Overrides**: Individual commands can override specific settings
4. **Defaults**: Hardcoded values in `Constants` class

### Configuration Structure

```yaml
# $HOME/.sokrates/config.yml
providers:
  - name: local
    type: openai
    api_endpoint: http://localhost:1234/v1
    api_key: notrequired
    default_model: qwen3-4b-instruct-2507
    default_temperature: 0.7

daemon:
  processing_interval: 15
  logfile_path: ~/.sokrates/logs/daemon.log
  file_watcher:
    enabled: false
    watched_directories: []
    file_extensions: [".txt", ".md"]

log_level: INFO
default_provider: local
```

### Validation

- Required configuration keys validated at startup
- Descriptive error messages for missing or invalid values
- Graceful degradation with sensible defaults where appropriate

---

## External Integrations

### LLM Endpoints

Sokrates integrates exclusively with **OpenAI-compatible REST APIs**:

| Provider | Endpoint Pattern | Authentication |
|----------|------------------|----------------|
| **LocalAI** | `http://localhost:xxxx/v1` | Optional API key |
| **Ollama** | `http://localhost:11434/v1` (via proxy) | None required |
| **LM Studio** | `http://localhost:1234/v1` | Optional API key |
| **Custom** | User-defined URL | Configured per provider |

All interactions use the standard OpenAI chat completion format.

### MCP Server Integration

An associated [MCP server](https://github.com/Kubementat/sokrates-mcp) enables integration via Model Context Protocol for use in AI assistants and IDEs. This is a separate repository and not part of the core Sokrates package.

---

## Deployment Considerations

### Primary Use Case: Local Development Tool

Sokrates is designed primarily as a **local development tool**:

- Runs on developer's machine (Linux, macOS, Windows)
- Requires Python 3.9+ runtime environment
- Installs via pip/uv as standard Python package
- Configuration stored in user home directory (`~/.sokrates`)

### Installation Methods

```bash
# Standard installation with uv
uv sync                # Install dependencies (basic version)
uv run sokrates --version

# With voice support enabled
uv sync --all-extras
uv run sokrates-chat   # Voice-enabled chat interface

# Development installation
uv pip install -e .    # Editable mode for development
```

### Environment Requirements

- **Python**: 3.9 or higher (modern type hints required)
- **Disk Space**: ~50MB base, additional space for SQLite database and logs
- **Memory**: Minimal footprint; streaming responses prevent large allocations
- **Network**: Required only when connecting to remote LLM endpoints

### No Cloud Deployment

Sokrates does not support server-side or cloud deployment scenarios:

- No containerization (Docker) required or provided
- No systemd service files included (daemon managed via CLI commands)
- Not designed for multi-user shared environments
- Configuration is per-user, not system-wide

---

## Performance Characteristics

### Typical Metrics

| Operation | Duration | Notes |
|-----------|----------|-------|
| **Simple prompt** | 1-3 seconds | Depends on model and network latency |
| **Code analysis** | 5-30 seconds | Scales with codebase size |
| **Batch processing** | Variable | Queue-based with retries |
| **Voice chat** | +2s overhead | Speech-to-text + TTS processing |

### Optimization Strategies

1. **Streaming Responses**: Reduces perceived latency, shows tokens as they arrive
2. **SQLite Indexing**: Fast task queue queries even with large history
3. **AST Parsing**: Efficient Python code analysis without full compilation
4. **Memory Management**: Stream reading for large files where possible

---

*This architecture document was generated as part of the Sokrates project specification process.*
