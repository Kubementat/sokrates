"""Unified CLI entry point for Sokrates.

This module defines the top-level Click group that registers all existing Sokrates
commands as subcommands under a single `sokrates` entry point, providing a
centralized, discoverable interface for all CLI functionality.
"""

import difflib
import importlib
import logging
import os
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Callable, Optional

import click

logger = logging.getLogger(__name__)


def is_first_time_user() -> bool:
    """Detect whether this is a first-time user by checking for the config file.

    Returns True when the Sokrates config file does not exist (i.e., the user has
    not yet configured Sokrates).  Returns False when the config file exists OR
    when config file existence cannot be determined (e.g., PermissionError).

    The config path is:
      * ``$SOKRATES_HOME_PATH/config.yml``  if the env var is set, otherwise
      * ``$HOME/.sokrates/config.yml``

    Returns:
        True if config.yml is missing (first-time user), False otherwise.
    """
    try:
        home_env = os.environ.get('SOKRATES_HOME_PATH')
        if home_env:
            config_path = Path(home_env) / 'config.yml'
        else:
            config_path = Path.home() / '.sokrates' / 'config.yml'
        return not config_path.exists()
    except Exception:
        # Permission errors or other OS failures: treat as "not first-time user"
        # so that we fail safe (no onboarding message) rather than crashing.
        return False

# ---------------------------------------------------------------------------
# Category-to-command mapping
# Defines the display order and grouping of commands in `sokrates --help`.
# Commands that are not yet registered (e.g., 'guide' before task-012) are
# silently skipped in the formatted output.
# ---------------------------------------------------------------------------

COMMAND_CATEGORIES: 'OrderedDict[str, list[str]]' = OrderedDict([
    ('Prompts', ['send-prompt', 'refine-prompt', 'refine-and-send-prompt']),
    ('Workflows', ['idea-generator', 'merge-ideas', 'generate-mantra', 'breakdown-task', 'execute-tasks']),
    ('Code Analysis', ['code-review', 'code-analyze', 'code-summarize', 'code-generate-tests']),
    ('Task Queue', ['task-add', 'task-list', 'task-status', 'task-remove', 'daemon']),
    ('Interactive', ['chat', 'guide']),
    ('Utilities', ['list-models', 'fetch-to-md']),
])


class CategorizedGroup(click.Group):
    """A Click Group subclass that displays commands grouped by category.

    When help is displayed, commands are shown under their assigned category
    headers (Prompts, Workflows, Code Analysis, Task Queue, Interactive, Utilities)
    rather than in a flat alphabetical list.  Commands not assigned to any
    category are shown in an "Other" section at the end.
    """

    def format_commands(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:  # type: ignore[override]
        """Write the grouped commands section into the help formatter.

        Args:
            ctx: The Click context.
            formatter: The help formatter to write into.
        """
        # Build a lookup of registered commands
        commands = self.commands or {}

        # Track which commands have been listed
        listed: set[str] = set()

        # Emit each category section
        for category, cmd_names in COMMAND_CATEGORIES.items():
            # Only include commands that are actually registered
            category_cmds: list[tuple[str, str]] = []
            for cmd_name in cmd_names:
                if cmd_name not in commands:
                    continue
                cmd = commands[cmd_name]
                # Use the command's short_help (derived from help parameter)
                help_text = cmd.get_short_help_str(limit=formatter.width or 80) if cmd else ''
                category_cmds.append((cmd_name, help_text))
                listed.add(cmd_name)

            if not category_cmds:
                continue

            with formatter.section(category):
                formatter.write_dl(category_cmds)

        # Emit any commands not in any category (safety net)
        unlisted = [(n, c) for n, c in commands.items() if n not in listed]
        if unlisted:
            other_cmds = []
            for cmd_name, cmd in unlisted:
                help_text = cmd.get_short_help_str(limit=formatter.width or 80) if cmd else ''
                other_cmds.append((cmd_name, help_text))

            with formatter.section('Other'):
                formatter.write_dl(other_cmds)

    def resolve_command(
        self, ctx: click.Context, args: list[str]
    ) -> 'tuple[str | None, click.Command | None, list[str]]':
        """Resolve a command name, providing enhanced error messages for unknown commands.

        When a command is not found, this method:
        - Suggests close matches using difflib fuzzy matching
        - Lists available commands grouped by category
        - Suggests running 'sokrates --help' for full documentation

        Args:
            ctx: The Click context.
            args: The remaining argument list.

        Returns:
            Tuple of (command_name, command, remaining_args).
        """
        cmd_name = args[0] if args else ''
        cmd = self.get_command(ctx, cmd_name)

        if cmd is not None or ctx.resilient_parsing:
            # Command found or in resilient parsing mode — delegate to parent
            return super().resolve_command(ctx, args)

        # Check for option-like argument (e.g., --help)
        if cmd_name.startswith('-'):
            return super().resolve_command(ctx, args)

        # Build enhanced error message for unknown command
        known_commands = list(self.commands.keys())
        close_matches = difflib.get_close_matches(cmd_name, known_commands, n=3, cutoff=0.5)

        # Build error message
        lines: list[str] = []
        lines.append(f"No such command '{cmd_name}'.")
        lines.append('')

        if close_matches:
            if len(close_matches) == 1:
                lines.append(f"Did you mean '{close_matches[0]}'?")
            else:
                formatted = ', '.join(f"'{m}'" for m in close_matches)
                lines.append(f'Did you mean one of: {formatted}?')
            lines.append('')

        # Add category listing
        lines.append('Available commands:')
        lines.append('')
        for category, cmd_names in COMMAND_CATEGORIES.items():
            available_in_category = [n for n in cmd_names if n in self.commands]
            if not available_in_category:
                continue
            lines.append(f'  {category}:')
            for name in available_in_category:
                lines.append(f'    sokrates {name}')
            lines.append('')

        lines.append("Run 'sokrates --help' for full documentation.")

        ctx.fail('\n'.join(lines))

_HELP_TEXT = """\
Sokrates — A CLI toolkit for effective LLM interactions.

Sokrates provides: prompt refinement and optimization, AI-powered code analysis
and review, a background task queue for long-running jobs, and interactive LLM
sessions. Works with any OpenAI-compatible endpoint (LocalAI, Ollama, LM Studio,
or custom deployments).

See the Interactive section below for an AI-powered introduction.
"""


def _make_lazy_command(
    name: str,
    module_path: str,
    fn_name: str,
    short_help: str = '',
    examples: str = '',
) -> click.Command:
    """Create a Click command that lazily loads and delegates to an argparse-based main().

    The underlying module is only imported when the command is actually invoked,
    preventing module-level side effects (e.g., config loading) from running at
    import time.

    Args:
        name: The subcommand name (without 'sokrates-' prefix).
        module_path: Dotted Python import path for the module containing main_fn.
        fn_name: Name of the callable to invoke inside the module (typically 'main').
        short_help: One-line description shown in the group help listing.
        examples: Optional example usage lines shown in the epilog.

    Returns:
        A Click Command that lazily delegates execution to the target function.
    """
    # Store examples separately so we can print them AFTER the options section
    # (required by the test: Options: must appear before Examples:).
    # The epilog is intentionally NOT set on the Click command — instead we
    # manually append it after the argparse options section in the help handler.
    examples_text = f'Examples:\n\n{examples}' if examples else None

    @click.command(
        name=name,
        help=short_help,
        epilog=None,
        add_help_option=False,
        context_settings=dict(
            allow_extra_args=True,
            allow_interspersed_args=False,
            ignore_unknown_options=True,
        ),
    )
    @click.argument('args', nargs=-1, type=click.UNPROCESSED)
    @click.pass_context
    def _command(ctx: click.Context, args: tuple) -> None:
        # If the user requested help, show Click usage/description, then argparse
        # detailed options, then Examples — so that Options: always precedes Examples:.
        if '--help' in args or '-h' in args:
            # Print the Click-level help (usage + description, no epilog)
            click.echo(ctx.get_help())
            click.echo()
            # Print argparse-level options (contains "options:" / "Options:" section).
            # Argparse calls sys.exit(0) after printing help, so we catch SystemExit
            # to allow the examples block to be appended afterwards.
            try:
                _invoke_main(module_path, fn_name, name, ['--help'])
            except SystemExit:
                pass
            # Print examples AFTER argparse options so Examples: always appears last
            if examples_text:
                click.echo()
                click.echo(examples_text)
            return

        # Reconstruct sys.argv so argparse inside the target main() sees the right args.
        # Use "sokrates <name>" as argv[0] so argparse usage output matches the unified
        # CLI format (e.g., "sokrates send-prompt" not "sokrates-send-prompt").
        _invoke_main(module_path, fn_name, name, list(args))

    return _command


def _invoke_main(module_path: str, fn_name: str, cmd_name: str, args: list[str]) -> None:
    """Lazily import a module and invoke its main function with the given args.

    Args:
        module_path: Dotted Python import path for the module.
        fn_name: Name of the callable to invoke.
        cmd_name: Subcommand name used in sys.argv[0].
        args: Argument list to pass (excluding argv[0]).
    """
    try:
        mod = importlib.import_module(module_path)
        main_fn: Callable = getattr(mod, fn_name)
    except ImportError as e:
        logger.error(f"Could not import module '{module_path}': {e}")
        click.echo(f"Error: command '{cmd_name}' could not be loaded ({e})", err=True)
        sys.exit(1)
    except AttributeError as e:
        logger.error(f"Could not find '{fn_name}' in '{module_path}': {e}")
        click.echo(f"Error: command '{cmd_name}' is misconfigured ({e})", err=True)
        sys.exit(1)

    sys.argv = [f'sokrates {cmd_name}'] + args
    main_fn()


_ONBOARDING_MESSAGE = """\
╔══════════════════════════════════════════════════════════════════╗
║  Welcome to Sokrates!  Getting started:                         ║
║                                                                  ║
║  It looks like this is your first time using Sokrates.           ║
║  Run 'sokrates guide' for an interactive introduction, or        ║
║  check the command list below to jump straight in.               ║
╚══════════════════════════════════════════════════════════════════╝
"""


@click.group(
    cls=CategorizedGroup,
    help=_HELP_TEXT,
    invoke_without_command=True,
    context_settings=dict(max_content_width=120),
)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Unified Sokrates CLI group.

    When invoked without a subcommand, displays help output.
    """
    if ctx.invoked_subcommand is None:
        if is_first_time_user():
            click.echo(_ONBOARDING_MESSAGE)
        click.echo(ctx.get_help())


# ---------------------------------------------------------------------------
# Command registry
# Each tuple: (subcommand-name, module-import-path, function-name, short-help, examples)
# Modules are imported lazily on first invocation — no side effects at import time.
# ---------------------------------------------------------------------------

_COMMAND_REGISTRY: list[tuple[str, str, str, str, str]] = [
    # ── Prompts ─────────────────────────────────────────────────────────────
    (
        'send-prompt',
        'sokrates.cli.sokrates_send_prompt',
        'main',
        'Send a prompt to an LLM endpoint and display the response.',
        '  sokrates send-prompt --prompt "Summarize quantum computing" --provider local',
    ),
    (
        'refine-prompt',
        'sokrates.cli.sokrates_refine_prompt',
        'main',
        'Refine and optimize a prompt using an LLM before sending.',
        '  sokrates refine-prompt --input-file prompt.md --provider local',
    ),
    (
        'refine-and-send-prompt',
        'sokrates.cli.sokrates_refine_and_send_prompt',
        'main',
        'Refine a prompt then send it to the LLM in one step.',
        '  sokrates refine-and-send-prompt --input-file prompt.md --provider local',
    ),
    # ── Workflows ────────────────────────────────────────────────────────────
    (
        'idea-generator',
        'sokrates.cli.sokrates_idea_generator',
        'main',
        'Generate ideas and content using multi-stage LLM workflows.',
        '  sokrates idea-generator --topic "AI ethics" --provider local',
    ),
    (
        'merge-ideas',
        'sokrates.cli.sokrates_merge_ideas',
        'main',
        'Merge and synthesize multiple idea documents into one.',
        '  sokrates merge-ideas --input-directory ./ideas --provider local',
    ),
    (
        'generate-mantra',
        'sokrates.cli.sokrates_generate_mantra',
        'main',
        'Generate a motivational mantra or affirmation using an LLM.',
        '  sokrates generate-mantra --provider local',
    ),
    (
        'breakdown-task',
        'sokrates.cli.sokrates_breakdown_task',
        'main',
        'Break down a complex task into actionable sub-tasks.',
        '  sokrates breakdown-task --task "Build a REST API" --provider local',
    ),
    (
        'execute-tasks',
        'sokrates.cli.sokrates_execute_tasks',
        'main',
        'Execute a list of tasks sequentially using an LLM.',
        '  sokrates execute-tasks --tasks-file tasks.json --provider local',
    ),
    # ── Code Analysis ────────────────────────────────────────────────────────
    (
        'code-review',
        'sokrates.cli.coding.sokrates_code_review',
        'main',
        'Perform an AI-powered code review on a Python codebase.',
        '  sokrates code-review --source-directory ./src --provider local',
    ),
    (
        'code-analyze',
        'sokrates.cli.coding.sokrates_code_analyze',
        'main',
        'Analyze a Python codebase for complexity and quality metrics.',
        '  sokrates code-analyze --source-directory ./src',
    ),
    (
        'code-summarize',
        'sokrates.cli.coding.sokrates_code_summarize',
        'main',
        'Generate a natural-language summary of a Python codebase.',
        '  sokrates code-summarize --source-directory ./src --provider local',
    ),
    (
        'code-generate-tests',
        'sokrates.cli.coding.sokrates_code_generate_tests',
        'main',
        'Generate unit tests for Python source files automatically.',
        '  sokrates code-generate-tests --source-directory ./src --provider local',
    ),
    # ── Task Queue ───────────────────────────────────────────────────────────
    (
        'task-add',
        'sokrates.cli.task_queue.sokrates_task_add',
        'main',
        'Add a task to the background processing queue.',
        '  sokrates task-add --task-file my_task.json --priority normal',
    ),
    (
        'task-list',
        'sokrates.cli.task_queue.sokrates_task_list',
        'main',
        'List all tasks in the background processing queue.',
        '  sokrates task-list',
    ),
    (
        'task-status',
        'sokrates.cli.task_queue.sokrates_task_status',
        'main',
        'Show the status of a specific task in the queue.',
        '  sokrates task-status --task-id 42',
    ),
    (
        'task-remove',
        'sokrates.cli.task_queue.sokrates_task_remove',
        'main',
        'Remove a task from the background processing queue.',
        '  sokrates task-remove --task-id 42',
    ),
    (
        'daemon',
        'sokrates.cli.task_queue.sokrates_daemon',
        'main',
        'Start, stop, or check the background task processing daemon.',
        '  sokrates daemon start\n  sokrates daemon stop\n  sokrates daemon status',
    ),
    # ── Interactive ──────────────────────────────────────────────────────────
    (
        'chat',
        'sokrates.cli.sokrates_chat',
        'main',
        'Start an interactive chat session with an LLM.',
        '  sokrates chat --provider local --model qwen3-4b-instruct',
    ),
    (
        'guide',
        'sokrates.cli.sokrates_guide',
        'main',
        'Start an interactive guide session with the Sokrates Teacher.',
        '  sokrates guide --provider local\n  sokrates guide --model qwen3-4b-instruct --provider local',
    ),
    # ── Utilities ────────────────────────────────────────────────────────────
    (
        'list-models',
        'sokrates.cli.sokrates_list_models',
        'main',
        'List available models from the configured LLM endpoint.',
        '  sokrates list-models --provider local',
    ),
    (
        'fetch-to-md',
        'sokrates.cli.sokrates_fetch_to_md',
        'main',
        'Fetch a URL and convert its content to Markdown.',
        '  sokrates fetch-to-md --url https://example.com --output page.md',
    ),
]

# Register all commands as lazy-loading Click commands.
# Each registration is wrapped in try/except so that a failure in one command
# (e.g., import error, missing optional dependency) does not prevent the remaining
# commands from loading successfully.
for _name, _module_path, _fn_name, _short_help, _examples in _COMMAND_REGISTRY:
    try:
        _cmd = _make_lazy_command(_name, _module_path, _fn_name, _short_help, _examples)
        cli.add_command(_cmd, name=_name)
    except ImportError as e:
        logger.warning(f"Could not load command '{_name}': {e}")


if __name__ == '__main__':
    cli()
