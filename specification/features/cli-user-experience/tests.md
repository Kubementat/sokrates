# Tests: CLI User Experience

This document defines integration and unit tests for the **cli-user-experience** feature, ensuring all behaviors work correctly.

---

## Integration Tests (User-facing command behavior)

### 0. Unified CLI Entry Point

#### Test: Unified entry point exists and responds
- **Type**: Integration
- **Setup**: Install Sokrates package
- **Action**: Run `sokrates --help` and capture output
- **Expected Results**:
  - Exit code is 0
  - Output contains usage information
  - Output lists available subcommands

#### Test: All existing commands registered as subcommands
- **Type**: Integration
- **Setup**: Install Sokrates package
- **Action**: Run `sokrates --help` and capture output
- **Expected Results**:
  - Output contains `chat` subcommand
  - Output contains `code-review` subcommand
  - Output contains `send-prompt` subcommand
  - Output contains `task-add` subcommand
  - Output contains `daemon` subcommand
  - Output contains `refine-and-send-prompt` subcommand
  - All commands from `[project.scripts]` are present (with `sokrates-` prefix removed)

#### Test: Subcommand names derived correctly from standalone names
- **Type**: Unit
- **Setup**: Import CLI group module
- **Action**: Inspect registered command names on the Click group
- **Expected Results**:
  - `sokrates-code-review` maps to subcommand name `code-review`
  - `sokrates-refine-and-send-prompt` maps to subcommand name `refine-and-send-prompt`
  - No subcommand retains the `sokrates-` prefix

#### Test: Standalone aliases still work
- **Type**: Integration
- **Setup**: Install Sokrates package
- **Action**: Run `sokrates-chat --help` and `sokrates chat --help`, compare outputs
- **Expected Results**:
  - Both commands produce equivalent help output
  - Both commands list the same options and arguments
  - Exit code is 0 for both

#### Test: Subcommand executes same logic as standalone
- **Type**: Integration
- **Setup**: Install Sokrates package, configure valid test environment
- **Action**: Run `sokrates list-models` and `sokrates-list-models`, compare outputs
- **Expected Results**:
  - Both commands produce identical output
  - Exit codes match

#### Test: Graceful handling of command registration failure
- **Type**: Unit
- **Setup**: Mock one command module to raise ImportError on import
- **Action**: Import the CLI group and list registered commands
- **Expected Results**:
  - The failing command is not registered (or shows a warning)
  - All other commands are still available and functional
  - No crash or unhandled exception

---

### 1. Central Command Discovery (`sokrates --help`)

#### Test: Display organized categories
- **Type**: Integration
- **Setup**: Install Sokrates with all subcommands registered
- **Action**: Run `sokrates --help` and capture output
- **Expected Results**:
  - Output contains category headers: "Prompts", "Workflows", "Code Analysis", "Task Queue", "Interactive", "Utilities"
  - Commands appear under their assigned category (e.g., `code-review` under "Code Analysis", `task-add` under "Task Queue")
  - Commands show brief one-line descriptions

#### Test: Project overview displayed at top
- **Type**: Integration
- **Setup**: Install Sokrates with all subcommands registered
- **Action**: Run `sokrates --help` and capture output
- **Expected Results**:
  - Output starts with project overview before command listings
  - Overview contains "Sokrates" and "CLI toolkit" or "LLM interactions"
  - Overview mentions core capabilities (prompt refinement, code analysis, task queue, interactive chat)
  - Overview contains suggestion to run `sokrates guide`

#### Test: All registered subcommands appear
- **Type**: Integration
- **Setup**: Ensure all existing subcommands are registered in the central CLI
- **Action**: Run `sokrates --help` and capture output
- **Expected Results**:
  - Output contains all known subcommands (code-review, task-add, daemon, etc.)
  - No registered commands are missing from help output

#### Test: First-time user onboarding message
- **Type**: Integration
- **Setup**: Create temporary home directory with no existing config file
- **Action**: Run `sokrates --help` with custom `SOKRATES_HOME_PATH`
- **Expected Results**:
  - Output contains brief onboarding note for new users
  - Message suggests trying `sokrates guide` for introduction

---

### 2. Subcommand Help with Examples

#### Test: Full usage instructions displayed
- **Type**: Integration
- **Setup**: No special setup required
- **Action**: Run `sokrates code-review --help` (or any existing subcommand)
- **Expected Results**:
  - Usage line shows correct command syntax
  - All options and parameters are listed with descriptions
  - Help text is formatted clearly with proper indentation

#### Test: Example snippets included via epilog
- **Type**: Integration
- **Setup**: No special setup required
- **Action**: Run `sokrates <subcommand> --help` for multiple subcommands
- **Expected Results**:
  - Each help output contains an "Examples:" section (rendered from Click's `epilog`)
  - Examples show complete, valid command syntax
  - At least one example per command is present
  - The examples section appears after the options listing

#### Test: Example validity
- **Type**: Integration
- **Setup**: No special setup required
- **Action**: Parse example commands from `sokrates <subcommand> --help` output
- **Expected Results**:
  - All examples use correct flag names (e.g., `-f`, not `--fix-flag`)
  - Examples reference real file paths or valid placeholders
  - No syntax errors in example commands

---

### 3. Unknown Command Handling

#### Test: Error message for unknown command
- **Type**: Integration
- **Setup**: No special setup required
- **Action**: Run `sokrates completely-unknown-command` and capture stderr
- **Expected Results**:
  - Exit code is non-zero (error)
  - Output contains error message with the unknown command name
  - Output includes a list of available commands grouped by category
  - Output includes suggestion to run `sokrates --help`

#### Test: Partial command suggestion via Click fuzzy matching
- **Type**: Integration
- **Setup**: No special setup required
- **Action**: Run `sokrates codr` and capture output
- **Expected Results**:
  - Output shows error message for the unknown command
  - Click's built-in fuzzy matching suggests `code-review` (or similar close match)
  - Available commands list is also shown

---

### 4. Interactive Guide Mode (`sokrates guide`)

#### Test: Guide mode starts successfully
- **Type**: Integration
- **Setup**: Configure valid LLM endpoint in test config
- **Action**: Run `sokrates guide` and send initial prompt "What can Sokrates do?"
- **Expected Results**:
  - Chat session starts without error
  - AI responds with overview of Sokrates capabilities
  - Response includes references to available commands

#### Test: Teacher persona in system prompt
- **Type**: Integration (via inspection)
- **Setup**: Mock LLM client that captures system prompt
- **Action**: Run `sokrates guide` and capture the system prompt sent to LLM
- **Expected Results**:
  - System prompt defines "Sokrates Teacher" role
  - Prompt includes instructions for explaining capabilities
  - Prompt includes guidance on command usage

#### Test: Capability query handling
- **Type**: Integration (via mock)
- **Setup**: Mock LLM client that returns predefined responses
- **Action**: Run `sokrates guide`, send "How do I review my code?", verify response
- **Expected Results**:
  - AI explains the `code-review` command purpose
  - Response includes example usage of `sokrates code-review`
  - Offers to help construct the actual command

#### Test: LLM unavailability fallback
- **Type**: Integration
- **Setup**: Configure invalid/unreachable LLM endpoint
- **Action**: Run `sokrates guide` and observe behavior
- **Expected Results**:
  - Error message appears instead of crash
  - Fallback text-based help menu is displayed containing:
    - A brief "What is Sokrates?" summary
    - Command categories with top commands and one-line descriptions
    - A suggestion to run `sokrates --help` for full documentation
    - A suggestion to check LLM endpoint configuration

#### Test: Exit with Ctrl+C
- **Type**: Integration (via mock)
- **Setup**: Mock LLM client for guide mode
- **Action**: Run `sokrates guide`, send a query, then exit with Ctrl+C
- **Expected Results**:
  - A goodbye message is displayed
  - Message suggests running `sokrates guide` again to restart
  - Process exits cleanly (no traceback or unhandled exception)

---

### 5. Chat Alias (`sokrates chat`)

#### Test: Chat subcommand starts successfully
- **Type**: Integration
- **Setup**: Configure valid LLM endpoint in test config
- **Action**: Run `sokrates chat` and send "Hello"
- **Expected Results**:
  - Chat session starts successfully
  - AI responds without error
  - Behavior is identical to the standalone `sokrates-chat` alias (covered by Behavior 0 alias tests)

#### Test: Standard persona (not teacher)
- **Type**: Integration (via inspection)
- **Setup**: Mock LLM client that captures system prompt for both commands
- **Action**: Run `sokrates chat`, capture system prompt, compare to guide mode
- **Expected Results**:
  - System prompt does NOT define "teacher" role
  - Prompt uses standard assistant persona
  - No onboarding or tutorial instructions in prompt

#### Test: Voice features optional
- **Type**: Integration
- **Setup**: Install Sokrates without voice dependencies
- **Action**: Run `sokrates chat` and verify operation
- **Expected Results**:
  - Chat works in text-only mode
  - No errors about missing voice libraries
  - User informed that voice features are not available (optional)

---

## Unit Tests (Internal components)

### 6. Command Registration System

#### Test: Commands correctly registered and discoverable
- **Type**: Unit
- **Setup**: Import command registration module, mock Click context
- **Action**: Call function to list all registered commands
- **Expected Results**:
  - Returns list of all subcommands with metadata
  - Each command has name, description, and category

#### Test: Command categories assigned properly
- **Type**: Unit
- **Setup**: Load all existing subcommands from configuration
- **Action**: Verify each command is assigned to correct category
- **Expected Results**:
  - `send-prompt`, `refine-prompt`, `refine-and-send-prompt` → "Prompts"
  - `idea-generator`, `merge-ideas`, `generate-mantra`, `breakdown-task`, `execute-tasks` → "Workflows"
  - `code-review`, `code-analyze`, `code-summarize`, `code-generate-tests` → "Code Analysis"
  - `task-add`, `task-list`, `task-status`, `task-remove`, `daemon` → "Task Queue"
  - `chat`, `guide` → "Interactive"
  - `list-models`, `fetch-to-md` → "Utilities"
  - All commands have exactly one category

#### Test: Example snippets attached to metadata
- **Type**: Unit
- **Setup**: Load command metadata for all subcommands
- **Action**: Verify each command has example_snippets field populated
- **Expected Results**:
  - Every registered command has at least one example
  - Examples are valid Python strings (not None or empty)

---

### 7. Help Formatter

#### Test: Consistent formatting across commands
- **Type**: Unit
- **Setup**: Mock Click context, prepare help output for multiple commands
- **Action**: Generate formatted help text for different subcommands
- **Expected Results**:
  - All outputs use same indentation style (2 or 4 spaces)
  - Category headers formatted consistently (bold/uppercase)
  - Examples section always appears at bottom of help

#### Test: Example section rendering
- **Type**: Unit
- **Setup**: Prepare command metadata with example snippets
- **Action**: Render examples section in help output
- **Expected Results**:
  - Examples prefixed with clear marker (e.g., "Examples:" header)
  - Each example on separate line, indented under header
  - Special characters properly escaped or quoted

#### Test: Line wrapping at max width
- **Type**: Unit
- **Setup**: Prepare long option descriptions (>80 chars)
- **Action**: Render help output with terminal width constraint
- **Expected Results**:
  - Lines wrap at 120 characters maximum
  - Wrapped lines maintain proper indentation
  - No broken words or awkward line breaks

---

### 8. Guide System Prompt Generator

#### Test: Role definition included
- **Type**: Unit
- **Setup**: Import system prompt generator module
- **Action**: Call function to generate guide mode system prompt
- **Expected Results**:
  - Output contains "Sokrates Teacher" role definition
  - Output contains "interactive guide" or equivalent phrasing

#### Test: Capabilities summary included
- **Type**: Unit
- **Setup**: Import system prompt generator module
- **Action**: Call function to generate guide mode system prompt, parse output
- **Expected Results**:
  - Prompt includes brief explanation of what Sokrates is
  - Core capabilities mentioned: prompt refinement, workflows, code analysis, task queue, interactive chat

#### Test: Command reference included
- **Type**: Unit
- **Setup**: Import system prompt generator module
- **Action**: Call function to generate guide mode system prompt, parse output
- **Expected Results**:
  - Prompt contains all six categories: Prompts, Workflows, Code Analysis, Task Queue, Interactive, Utilities
  - Prompt contains all commands from the category mapping (e.g., `send-prompt`, `code-review`, `task-add`, etc.)

#### Test: Behavioral instructions included
- **Type**: Unit
- **Setup**: Import system prompt generator module
- **Action**: Call function to generate guide mode system prompt
- **Expected Results**:
  - Instructions for providing practical examples when explaining commands are present
  - Instructions for matching user goals to relevant commands are present
  - Instructions for keeping responses concise and actionable are present

#### Test: Fallback text menu generation
- **Type**: Unit
- **Setup**: Import fallback menu generator module
- **Action**: Call function to generate text-based help menu when LLM unavailable
- **Expected Results**:
  - Output contains a brief "What is Sokrates?" summary
  - Output contains command categories with top commands and one-line descriptions
  - Output contains suggestion to run `sokrates --help`
  - Output contains suggestion to check LLM endpoint configuration
  - Format is readable in terminal (no markdown dependencies)

---

## Edge Case Tests

### 9. First-Time User Experience

#### Test: Missing config detection
- **Type**: Unit
- **Setup**: Create temporary home directory, ensure no config file exists
- **Action**: Call function that checks for first-time user status
- **Expected Results**:
  - Function returns `True` when config file missing
  - No errors or exceptions during check

#### Test: Onboarding message disappears when config exists
- **Type**: Integration
- **Setup**: Temporary home directory, no config initially
- **Action**: Run `sokrates --help` (no config), then create a minimal `config.yml`, then run `sokrates --help` again
- **Expected Results**:
  - First run (no config) shows onboarding note in help output
  - Second run (config exists) does NOT show onboarding note

---

### 10. AI Agent Usage Patterns

#### Test: Parseable help output
- **Type**: Integration
- **Setup**: No special setup required
- **Action**: Run `sokrates --help` and parse output programmatically
- **Expected Results**:
  - Output can be split by category headers reliably
  - Command names are clearly identifiable in each section
  - No dynamic content (timestamps, random IDs) that breaks parsing

#### Test: Consistent command metadata
- **Type**: Unit
- **Setup**: Load all command metadata from registration system
- **Action**: Verify consistency across all commands
- **Expected Results**:
  - All commands have same fields in metadata structure
  - Field types are consistent (e.g., descriptions always strings)
  - No missing required fields for any command

---

## Test Setup Requirements

### Fixtures Needed

#### CLI Runner Fixture
```python
import pytest
from click.testing import CliRunner

@pytest.fixture
def runner():
    """Click test client for Sokrates CLI."""
    return CliRunner()
```

#### Temporary Config Directory
```python
import tempfile
import os

@pytest.fixture
def temp_home():
    """Create temporary home directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_home = os.environ.get('SOKRATES_HOME_PATH')
        os.environ['SOKRATES_HOME_PATH'] = tmpdir
        yield tmpdir
        if old_home is not None:
            os.environ['SOKRATES_HOME_PATH'] = old_home
        else:
            os.environ.pop('SOKRATES_HOME_PATH', None)
```

#### Mock LLM Client for Guide Mode
```python
from unittest.mock import Mock, MagicMock

@pytest.fixture
def mock_llm_client():
    """Mock OpenAI client for testing guide mode without real API calls."""
    mock = MagicMock()
    mock.chat.completions.create.return_value.choices[0].message.content = "Mock response"
    return mock
```

### Environment Variables to Set

- `SOKRATES_HOME_PATH`: Path to test temporary directory (set via fixture)
- `OPENAI_API_KEY`: Required for chat/guide functionality tests (can be dummy value like "test-key")
- `LLM_API_ENDPOINT`: Test endpoint URL (can point to mock server or use default)

---

*This tests document was generated as part of the Sokrates feature specification process.*
