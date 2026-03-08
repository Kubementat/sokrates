# Behaviors: CLI User Experience

This document defines the discrete behaviors for the **cli-user-experience** feature, which provides a centralized CLI interface for Sokrates with improved discoverability and interactive guidance.

---

## 0. Unified CLI Entry Point

### Overview
Currently Sokrates exposes each command as a separate executable (e.g., `sokrates-chat`, `sokrates-code-review`, `sokrates-task-add`). This behavior introduces a single unified `sokrates` Click group that registers all existing commands as subcommands, providing a single discoverable entry point.

### Happy Path
- A new Click group entry point `sokrates` is created (e.g., `sokrates.cli:cli`)
- All existing CLI commands are registered as subcommands of this group, with names derived by dropping the `sokrates-` prefix:
  - `sokrates-chat` → `sokrates chat`
  - `sokrates-code-review` → `sokrates code-review`
  - `sokrates-send-prompt` → `sokrates send-prompt`
  - `sokrates-task-add` → `sokrates task-add`
  - `sokrates-daemon` → `sokrates daemon`
  - (and all other existing commands following the same pattern)
- The new entry point is added to `[project.scripts]` in `pyproject.toml` as: `sokrates = "sokrates.cli:cli"`
- Running `sokrates` without arguments shows the grouped help output (see Behavior 1)

### Backward Compatibility
- All existing standalone entry points (`sokrates-chat`, `sokrates-code-review`, etc.) are **preserved as aliases** in `[project.scripts]` so that existing scripts and workflows continue to work
- The standalone commands behave identically to their subcommand counterparts

### Implementation Details
- The unified group is defined as a `@click.group()` in `src/sokrates/cli/__init__.py` (or a new dedicated module such as `src/sokrates/cli/main.py`)
- Each existing command's `main` function is registered via `cli.add_command(main, name='<subcommand-name>')`
- New commands introduced by this feature (`guide`, `chat`) are registered in the same group

### Error Cases
- If a command fails to register (e.g., import error in one module), the remaining commands must still load — use lazy loading or catch import errors per command with a warning

### Edge Cases
- Subcommand names with multiple hyphens (e.g., `sokrates-refine-and-send-prompt` → `sokrates refine-and-send-prompt`) are preserved as-is after prefix removal
- If a user runs a standalone alias (e.g., `sokrates-chat`), it behaves exactly like `sokrates chat` — same options, same output

---

## 1. Central Command Discovery (`sokrates --help`)

### Happy Path
- When a user runs `sokrates` or `sokrates --help`, the system displays an organized list of all available subcommands grouped by category
- Each command shows a brief one-line description explaining its purpose
- The output includes a project overview at the top explaining what Sokrates is, set via the Click group's `help` parameter, containing:
  - One-line summary: "Sokrates — A CLI toolkit for effective LLM interactions"
  - 2–3 sentences describing core capabilities (prompt refinement, code analysis, task queue, interactive chat)
  - A note to run `sokrates guide` for an interactive introduction
- The categories and their assigned commands are:

| Category | Commands |
|---|---|
| **Prompts** | `send-prompt`, `refine-prompt`, `refine-and-send-prompt` |
| **Workflows** | `idea-generator`, `merge-ideas`, `generate-mantra`, `breakdown-task`, `execute-tasks` |
| **Code Analysis** | `code-review`, `code-analyze`, `code-summarize`, `code-generate-tests` |
| **Task Queue** | `task-add`, `task-list`, `task-status`, `task-remove`, `daemon` |
| **Interactive** | `chat`, `guide` |
| **Utilities** | `list-models`, `fetch-to-md` |

### Error Cases
- If no commands are registered (unusual installation issue), display friendly error message suggesting to check installation
- If help output exceeds terminal width, implement proper line wrapping and pagination suggestions

### Edge Cases
- First-time users: Detect if `$HOME/.sokrates/config.yml` doesn't exist and show brief onboarding note
- Terminal with limited width: Ensure formatting remains readable (max 120 chars per line)

---

## 2. Subcommand Help (`sokrates <subcommand> --help`)

### Happy Path
- Running `sokrates <subcommand> --help` displays full usage instructions for that specific command
- Shows all available options, parameters, and their descriptions in a clear format
- **Required**: Each help output must include at least one complete usage example snippet showing real-world application
- Examples are attached via Click's `epilog` parameter on `@click.command()`, which displays after the options section
- Each command's `epilog` contains an "Examples:" header followed by one or more usage examples
- Examples use correct command syntax with available flags and arguments

### Error Cases
- If subcommand doesn't exist, show "Unknown command" error with list of valid alternatives
- If required arguments are missing in the main help, clearly indicate they are required (not optional)

### Edge Cases
- Commands with many options: Group related options together for readability
- Long option descriptions: Wrap text at 120 characters maximum
- Examples with special characters: Escape properly in help output

---

## 3. Unknown Command Handling (`sokrates <unknown>`)

### Happy Path
- When a user runs an unknown command like `sokrates unknown-command`, Click's built-in error handling displays an error message (e.g., "Error: No such command 'unknown-command'")
- Click's built-in fuzzy matching (via `difflib.get_close_matches`) suggests close matches when available (e.g., `sokrates codr` → suggests `code-review`)
- In addition to Click's default error, the output includes:
  - A list of available commands grouped by category to help the user find what they need
  - A suggestion to run `sokrates --help` for complete documentation
- This is implemented by overriding the Click group's error handling (e.g., custom `resolve_command` or `format_usage` on the group)

### Edge Cases
- Empty command input: Treat as no command provided, show main help instead of error
- Command with invalid characters: Click handles character validation; no custom logic needed

---

## 4. Interactive Guide Mode (`sokrates guide`)

### Happy Path
- Running `sokrates guide` starts an interactive chat session that serves as a "Sokrates Teacher"
- Uses existing `sokrates-chat` command infrastructure (voice features, LLM interaction)
- The system prompt sent to the LLM must include the following structured content:
  1. **Role definition**: "You are the Sokrates Teacher, an interactive guide for the Sokrates CLI toolkit."
  2. **Capabilities summary**: A brief description of Sokrates and its core capabilities (prompt refinement, workflows, code analysis, task queue, interactive chat)
  3. **Command reference**: The full category-to-command mapping:
     - Prompts: `send-prompt`, `refine-prompt`, `refine-and-send-prompt`
     - Workflows: `idea-generator`, `merge-ideas`, `generate-mantra`, `breakdown-task`, `execute-tasks`
     - Code Analysis: `code-review`, `code-analyze`, `code-summarize`, `code-generate-tests`
     - Task Queue: `task-add`, `task-list`, `task-status`, `task-remove`, `daemon`
     - Interactive: `chat`, `guide`
     - Utilities: `list-models`, `fetch-to-md`
  4. **Behavioral instructions**: Provide practical examples when explaining commands, match user goals to relevant commands, keep responses concise and actionable

### User Interaction Scenarios
- **Query about capabilities**: User types "What can Sokrates do?" → AI lists main capabilities with command references
- **Command-specific help**: User types "How do I review my code?" → AI explains `code-review` command, shows examples, offers to help construct the command
- **Workflow guidance**: User types "I have a long-running task" → AI suggests using task queue system with examples

### Error Cases
- If LLM endpoint is unavailable during guide mode, show graceful error message and provide a static fallback text-based help menu containing:
  - A brief "What is Sokrates?" summary (1–2 sentences)
  - A list of command categories with their top commands and one-line descriptions (matching the categories from Behavior 1)
  - A suggestion to run `sokrates --help` for full documentation and to check the LLM endpoint configuration
- If user exits guide mode mid-session (Ctrl+C), display a goodbye message and suggest running `sokrates guide` again to restart

### Edge Cases
- First-time users: Detect missing config and offer onboarding overview before diving into detailed guidance
- Voice features not installed: Guide mode works in text-only mode without voice capabilities

---

## 5. Chat Alias (`sokrates chat`)

### Happy Path
- `sokrates chat` is the subcommand registration of the existing `sokrates-chat` logic (registered via Behavior 0's unified CLI group)
- Provides full interactive chat functionality (voice-enabled if voice features are installed)
- Uses standard LLM interaction without "teacher/guide" persona — behaves like a regular assistant

### Error Cases
- If voice features not installed, proceed with text-only chat mode
- If LLM endpoint unavailable during chat, show error and suggest checking endpoint configuration

### Edge Cases
- `sokrates chat` and `sokrates guide` are separate CLI invocations with no shared session state
- Voice features optional: Chat works regardless of voice installation status

---

## 6. AI Agent Discoverability

### Happy Path
- All help output is formatted consistently for programmatic consumption by AI agents
- Command descriptions and examples are clear and unambiguous
- No dynamic content that would break parsing (e.g., timestamps, random elements)

### Edge Cases
- AI agents querying via shell scripts: Ensure consistent output formatting across runs
- Non-interactive environments: All features work in headless mode for automation

---

## 7. Onboarding Experience

### Happy Path
- When `$SOKRATES_HOME_PATH/config.yml` (default `$HOME/.sokrates/config.yml`) does not exist, a brief onboarding message is shown at the top of the `sokrates --help` output
- Message explains core capabilities without overwhelming the user
- Suggests trying `sokrates guide` for interactive introduction
- Once the config file exists (created manually or through any setup process), the onboarding message no longer appears

### Error Cases
- If detection of config file existence fails (e.g., permission error), proceed with standard help without onboarding message (no breaking changes)
- Onboarding message doesn't block experienced users from seeing full command list

---

*This behaviors document was generated as part of the Sokrates feature specification process.*
