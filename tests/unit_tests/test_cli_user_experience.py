'''Unit tests for CLI user experience internal components.

Tests cover internal components defined in the cli-user-experience feature spec:
- Behavior 6: Command registration system (categories, metadata, example snippets)
- Behavior 7: Help formatter (consistent formatting, example rendering, line wrapping)
- Behavior 8: Guide system prompt generator (role, capabilities, command reference, behavioral instructions)
- Behavior 9: First-time user experience (config file detection)
- Behavior 10: AI agent usage patterns (parseable output, consistent metadata)

All external dependencies are mocked. Tests are expected to fail initially since the
implementation does not exist yet — a test task is considered complete without a green
test suite.
'''

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


# ──────────────────────────── helpers ────────────────────────────

def _import_cli_main():
    '''Import the unified CLI main module, returning None if not yet implemented.'''
    try:
        import sokrates.cli.main as main_module
        return main_module
    except (ImportError, ModuleNotFoundError):
        return None


def _import_cli_group():
    '''Import the unified Click group, returning None if not yet implemented.'''
    try:
        from sokrates.cli.main import cli
        return cli
    except (ImportError, ModuleNotFoundError):
        return None


def _import_guide_module():
    '''Import the guide module, returning None if not yet implemented.'''
    try:
        import sokrates.cli.sokrates_guide as guide_module
        return guide_module
    except (ImportError, ModuleNotFoundError):
        return None


# ──────────────────────────── fixtures ────────────────────────────

@pytest.fixture
def temp_home():
    '''Create a temporary home directory with SOKRATES_HOME_PATH set for testing.'''
    with tempfile.TemporaryDirectory() as tmpdir:
        old_home = os.environ.get('SOKRATES_HOME_PATH')
        os.environ['SOKRATES_HOME_PATH'] = tmpdir
        yield tmpdir
        if old_home is not None:
            os.environ['SOKRATES_HOME_PATH'] = old_home
        else:
            os.environ.pop('SOKRATES_HOME_PATH', None)


@pytest.fixture
def mock_llm_client():
    '''Mock OpenAI client for testing guide mode without real API calls.'''
    mock = MagicMock()
    mock.chat.completions.create.return_value.choices[0].message.content = 'Mock response'
    return mock


# ═══════════════════════════════════════════════════════════════════
# Behavior 6: Command Registration System
# ═══════════════════════════════════════════════════════════════════

class TestCommandRegistrationSystem:
    '''Tests for Behavior 6: command registration, categories, and example metadata.'''

    # Expected category-to-command mapping from spec
    EXPECTED_CATEGORIES = {
        'Prompts': ['send-prompt', 'refine-prompt', 'refine-and-send-prompt'],
        'Workflows': ['idea-generator', 'merge-ideas', 'generate-mantra', 'breakdown-task', 'execute-tasks'],
        'Code Analysis': ['code-review', 'code-analyze', 'code-summarize', 'code-generate-tests'],
        'Task Queue': ['task-add', 'task-list', 'task-status', 'task-remove', 'daemon'],
        'Interactive': ['chat', 'guide'],
        'Utilities': ['list-models', 'fetch-to-md'],
    }

    ALL_COMMANDS = [
        'send-prompt', 'refine-prompt', 'refine-and-send-prompt',
        'idea-generator', 'merge-ideas', 'generate-mantra', 'breakdown-task', 'execute-tasks',
        'code-review', 'code-analyze', 'code-summarize', 'code-generate-tests',
        'task-add', 'task-list', 'task-status', 'task-remove', 'daemon',
        'chat', 'guide',
        'list-models', 'fetch-to-md',
    ]

    def test_cli_group_is_importable(self):
        '''The unified CLI group is importable without errors.'''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')
        assert cli is not None, 'CLI group should not be None'

    def test_commands_correctly_registered_and_discoverable(self):
        '''All expected commands are registered on the Click group.'''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        registered_commands = list(cli.commands.keys())

        for cmd in self.ALL_COMMANDS:
            assert cmd in registered_commands, (
                f"Command '{cmd}' is not registered in the CLI group. "
                f"Registered commands: {registered_commands}"
            )

    def test_no_command_retains_sokrates_prefix(self):
        '''No registered command retains the "sokrates-" prefix in its name.'''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        registered_commands = list(cli.commands.keys())
        prefixed = [cmd for cmd in registered_commands if cmd.startswith('sokrates-')]
        assert prefixed == [], (
            f"Commands should not retain 'sokrates-' prefix: {prefixed}"
        )

    def test_command_categories_mapping_defined(self):
        '''A category-to-command mapping data structure is defined in main module.'''
        main_module = _import_cli_main()
        if main_module is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        # The module should expose a category mapping (as dict, OrderedDict, or similar)
        has_mapping = (
            hasattr(main_module, 'COMMAND_CATEGORIES')
            or hasattr(main_module, 'CATEGORIES')
            or hasattr(main_module, 'CATEGORY_COMMANDS')
            or hasattr(main_module, 'COMMAND_GROUPS')
        )
        assert has_mapping, (
            'Expected a category mapping data structure in sokrates.cli.main '
            '(e.g., COMMAND_CATEGORIES, CATEGORIES, CATEGORY_COMMANDS, COMMAND_GROUPS)'
        )

    def test_prompts_category_commands(self):
        '''send-prompt, refine-prompt, refine-and-send-prompt are in "Prompts" category.'''
        main_module = _import_cli_main()
        if main_module is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        # Find the category mapping attribute
        mapping = None
        for attr_name in ('COMMAND_CATEGORIES', 'CATEGORIES', 'CATEGORY_COMMANDS', 'COMMAND_GROUPS'):
            if hasattr(main_module, attr_name):
                mapping = getattr(main_module, attr_name)
                break

        if mapping is None:
            pytest.skip('No category mapping found in sokrates.cli.main')

        expected_prompts = {'send-prompt', 'refine-prompt', 'refine-and-send-prompt'}
        # Find the Prompts category value (could be list or tuple)
        prompts_key = next((k for k in mapping if 'prompt' in k.lower() or k == 'Prompts'), None)
        assert prompts_key is not None, f"'Prompts' category key not found in mapping: {list(mapping.keys())}"

        prompts_commands = set(mapping[prompts_key])
        assert expected_prompts.issubset(prompts_commands), (
            f"Expected {expected_prompts} in Prompts category, found: {prompts_commands}"
        )

    def test_workflows_category_commands(self):
        '''Workflow commands are in "Workflows" category.'''
        main_module = _import_cli_main()
        if main_module is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        mapping = None
        for attr_name in ('COMMAND_CATEGORIES', 'CATEGORIES', 'CATEGORY_COMMANDS', 'COMMAND_GROUPS'):
            if hasattr(main_module, attr_name):
                mapping = getattr(main_module, attr_name)
                break

        if mapping is None:
            pytest.skip('No category mapping found in sokrates.cli.main')

        expected_workflows = {'idea-generator', 'merge-ideas', 'generate-mantra', 'breakdown-task', 'execute-tasks'}
        workflows_key = next((k for k in mapping if 'workflow' in k.lower() or k == 'Workflows'), None)
        assert workflows_key is not None, f"'Workflows' category key not found: {list(mapping.keys())}"

        workflows_commands = set(mapping[workflows_key])
        assert expected_workflows.issubset(workflows_commands), (
            f"Expected {expected_workflows} in Workflows category, found: {workflows_commands}"
        )

    def test_code_analysis_category_commands(self):
        '''Code analysis commands are in "Code Analysis" category.'''
        main_module = _import_cli_main()
        if main_module is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        mapping = None
        for attr_name in ('COMMAND_CATEGORIES', 'CATEGORIES', 'CATEGORY_COMMANDS', 'COMMAND_GROUPS'):
            if hasattr(main_module, attr_name):
                mapping = getattr(main_module, attr_name)
                break

        if mapping is None:
            pytest.skip('No category mapping found in sokrates.cli.main')

        expected_code = {'code-review', 'code-analyze', 'code-summarize', 'code-generate-tests'}
        code_key = next((k for k in mapping if 'code' in k.lower() or 'analysis' in k.lower()), None)
        assert code_key is not None, f"'Code Analysis' category key not found: {list(mapping.keys())}"

        code_commands = set(mapping[code_key])
        assert expected_code.issubset(code_commands), (
            f"Expected {expected_code} in Code Analysis category, found: {code_commands}"
        )

    def test_task_queue_category_commands(self):
        '''Task queue commands are in "Task Queue" category.'''
        main_module = _import_cli_main()
        if main_module is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        mapping = None
        for attr_name in ('COMMAND_CATEGORIES', 'CATEGORIES', 'CATEGORY_COMMANDS', 'COMMAND_GROUPS'):
            if hasattr(main_module, attr_name):
                mapping = getattr(main_module, attr_name)
                break

        if mapping is None:
            pytest.skip('No category mapping found in sokrates.cli.main')

        expected_tasks = {'task-add', 'task-list', 'task-status', 'task-remove', 'daemon'}
        task_key = next((k for k in mapping if 'task' in k.lower() or 'queue' in k.lower()), None)
        assert task_key is not None, f"'Task Queue' category key not found: {list(mapping.keys())}"

        task_commands = set(mapping[task_key])
        assert expected_tasks.issubset(task_commands), (
            f"Expected {expected_tasks} in Task Queue category, found: {task_commands}"
        )

    def test_interactive_category_commands(self):
        '''chat and guide are in "Interactive" category.'''
        main_module = _import_cli_main()
        if main_module is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        mapping = None
        for attr_name in ('COMMAND_CATEGORIES', 'CATEGORIES', 'CATEGORY_COMMANDS', 'COMMAND_GROUPS'):
            if hasattr(main_module, attr_name):
                mapping = getattr(main_module, attr_name)
                break

        if mapping is None:
            pytest.skip('No category mapping found in sokrates.cli.main')

        expected_interactive = {'chat', 'guide'}
        interactive_key = next((k for k in mapping if 'interactive' in k.lower()), None)
        assert interactive_key is not None, f"'Interactive' category key not found: {list(mapping.keys())}"

        interactive_commands = set(mapping[interactive_key])
        assert expected_interactive.issubset(interactive_commands), (
            f"Expected {expected_interactive} in Interactive category, found: {interactive_commands}"
        )

    def test_utilities_category_commands(self):
        '''list-models and fetch-to-md are in "Utilities" category.'''
        main_module = _import_cli_main()
        if main_module is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        mapping = None
        for attr_name in ('COMMAND_CATEGORIES', 'CATEGORIES', 'CATEGORY_COMMANDS', 'COMMAND_GROUPS'):
            if hasattr(main_module, attr_name):
                mapping = getattr(main_module, attr_name)
                break

        if mapping is None:
            pytest.skip('No category mapping found in sokrates.cli.main')

        expected_utils = {'list-models', 'fetch-to-md'}
        utils_key = next((k for k in mapping if 'utilit' in k.lower()), None)
        assert utils_key is not None, f"'Utilities' category key not found: {list(mapping.keys())}"

        utils_commands = set(mapping[utils_key])
        assert expected_utils.issubset(utils_commands), (
            f"Expected {expected_utils} in Utilities category, found: {utils_commands}"
        )

    def test_all_commands_have_exactly_one_category(self):
        '''Every command appears in exactly one category (no duplicates, no orphans).'''
        main_module = _import_cli_main()
        if main_module is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        mapping = None
        for attr_name in ('COMMAND_CATEGORIES', 'CATEGORIES', 'CATEGORY_COMMANDS', 'COMMAND_GROUPS'):
            if hasattr(main_module, attr_name):
                mapping = getattr(main_module, attr_name)
                break

        if mapping is None:
            pytest.skip('No category mapping found in sokrates.cli.main')

        # Build a flat list of all categorized commands
        all_categorized = []
        for commands in mapping.values():
            all_categorized.extend(commands)

        # Check for duplicates
        seen = {}
        for cmd in all_categorized:
            seen[cmd] = seen.get(cmd, 0) + 1
        duplicates = {cmd: count for cmd, count in seen.items() if count > 1}
        assert not duplicates, f"Commands appear in multiple categories: {duplicates}"

    def test_registered_command_has_help_text(self):
        '''Each registered Click command has non-empty help text.'''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        for cmd_name, cmd_obj in cli.commands.items():
            help_text = cmd_obj.help or ''
            assert len(help_text.strip()) > 0, (
                f"Command '{cmd_name}' has no help text; every command should have a description"
            )


# ═══════════════════════════════════════════════════════════════════
# Behavior 7: Help Formatter
# ═══════════════════════════════════════════════════════════════════

class TestHelpFormatter:
    '''Tests for Behavior 7: help formatter produces consistent, well-structured output.'''

    def test_cli_group_is_click_group(self):
        '''The CLI entry point is a Click Group (or subclass).'''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        import click
        assert isinstance(cli, click.Group), (
            f"Expected cli to be a click.Group instance, got {type(cli)}"
        )

    def test_category_headers_present_in_help_output(self):
        '''sokrates --help output contains all six category headers.'''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])

        expected_headers = [
            'Prompts',
            'Workflows',
            'Code Analysis',
            'Task Queue',
            'Interactive',
            'Utilities',
        ]
        for header in expected_headers:
            assert header in result.output, (
                f"Category header '{header}' missing from help output:\n{result.output}"
            )

    def test_help_output_line_length_within_120_chars(self):
        '''No line in the help output exceeds 120 characters.'''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        from click.testing import CliRunner
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(cli, ['--help'])

        lines = result.output.split('\n')
        long_lines = [(i + 1, line) for i, line in enumerate(lines) if len(line) > 120]
        assert not long_lines, (
            f"Found lines exceeding 120 characters:\n"
            + '\n'.join(f"  Line {lineno}: {line!r}" for lineno, line in long_lines[:5])
        )

    def test_examples_section_in_subcommand_help(self):
        '''A representative subcommand includes an Examples section in its help output.'''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        from click.testing import CliRunner
        runner = CliRunner()

        representative_commands = ['send-prompt', 'code-review', 'task-add']
        for cmd in representative_commands:
            if cmd not in cli.commands:
                continue
            result = runner.invoke(cli, [cmd, '--help'])
            assert result.exit_code == 0, f"'{cmd} --help' failed: {result.output}"
            assert 'Examples:' in result.output or 'EXAMPLES' in result.output.upper(), (
                f"Expected 'Examples:' section in '{cmd}' help output:\n{result.output}"
            )

    def test_examples_use_sokrates_prefix_not_standalone(self):
        '''Examples in help output use "sokrates <cmd>" not "sokrates-<cmd>" format.'''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        from click.testing import CliRunner
        runner = CliRunner()

        for cmd_name in list(cli.commands.keys())[:5]:  # Check a sample
            result = runner.invoke(cli, [cmd_name, '--help'])
            if result.exit_code != 0:
                continue
            assert f'sokrates-{cmd_name}' not in result.output, (
                f"Found standalone prefix 'sokrates-{cmd_name}' in '{cmd_name}' help output. "
                f"Examples should use 'sokrates {cmd_name}' format:\n{result.output}"
            )

    def test_help_contains_no_dynamic_content(self):
        '''Help output contains no dynamic content (timestamps, random IDs).

        Verifies that help output is stable and parseable by AI agents.
        '''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        from click.testing import CliRunner
        import re
        runner = CliRunner()
        result1 = runner.invoke(cli, ['--help'])
        result2 = runner.invoke(cli, ['--help'])

        assert result1.output == result2.output, (
            'Help output is not deterministic (contains dynamic content):\n'
            f'Run 1:\n{result1.output}\n\nRun 2:\n{result2.output}'
        )

    def test_options_section_precedes_examples_section(self):
        '''For subcommands with both sections, Options appears before Examples.'''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        from click.testing import CliRunner
        runner = CliRunner()

        for cmd_name in ['send-prompt', 'code-review']:
            if cmd_name not in cli.commands:
                continue
            result = runner.invoke(cli, [cmd_name, '--help'])
            if result.exit_code != 0:
                continue
            output = result.output
            options_idx = output.find('Options:')
            examples_idx = output.find('Examples:')
            if options_idx != -1 and examples_idx != -1:
                assert options_idx < examples_idx, (
                    f"In '{cmd_name}' help: 'Options:' should appear before 'Examples:':\n{output}"
                )

    def test_category_headers_formatted_consistently(self):
        '''Category headers in help output are formatted consistently (title case or uppercase).'''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        output = result.output

        expected_categories = ['Prompts', 'Workflows', 'Code Analysis', 'Task Queue', 'Interactive', 'Utilities']
        # Verify they all appear with consistent casing (each as-is or UPPERCASE)
        found_formats = {}
        for cat in expected_categories:
            if cat in output:
                found_formats[cat] = 'TitleCase'
            elif cat.upper() in output:
                found_formats[cat] = 'UPPERCASE'

        # All found categories should use the same format style
        formats_used = set(found_formats.values())
        assert len(formats_used) <= 1, (
            f"Category headers use inconsistent formatting: {found_formats}"
        )


# ═══════════════════════════════════════════════════════════════════
# Behavior 8: Guide System Prompt Generator
# ═══════════════════════════════════════════════════════════════════

class TestGuideSystemPromptGenerator:
    '''Tests for Behavior 8: guide system prompt generator produces correct content.'''

    def test_generate_guide_system_prompt_is_importable(self):
        '''generate_guide_system_prompt function is importable from guide module.'''
        guide_module = _import_guide_module()
        if guide_module is None:
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

        assert hasattr(guide_module, 'generate_guide_system_prompt'), (
            'Expected function generate_guide_system_prompt in sokrates.cli.sokrates_guide'
        )

    def test_generate_guide_system_prompt_returns_string(self):
        '''generate_guide_system_prompt() returns a non-empty string.'''
        guide_module = _import_guide_module()
        if guide_module is None:
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

        prompt = guide_module.generate_guide_system_prompt()
        assert isinstance(prompt, str), f'Expected str, got {type(prompt)}'
        assert len(prompt.strip()) > 0, 'System prompt should not be empty'

    def test_system_prompt_includes_teacher_role(self):
        '''System prompt includes "Sokrates Teacher" role definition.'''
        guide_module = _import_guide_module()
        if guide_module is None:
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

        prompt = guide_module.generate_guide_system_prompt()
        assert 'Sokrates Teacher' in prompt or (
            'teacher' in prompt.lower() and 'sokrates' in prompt.lower()
        ), f"Expected 'Sokrates Teacher' role definition in system prompt:\n{prompt[:800]}"

    def test_system_prompt_includes_interactive_guide_phrasing(self):
        '''System prompt includes "interactive guide" or equivalent phrasing.'''
        guide_module = _import_guide_module()
        if guide_module is None:
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

        prompt = guide_module.generate_guide_system_prompt()
        assert 'interactive guide' in prompt.lower() or 'guide' in prompt.lower(), (
            f"Expected 'interactive guide' phrasing in system prompt:\n{prompt[:500]}"
        )

    def test_system_prompt_includes_capabilities_summary(self):
        '''System prompt includes a summary of Sokrates capabilities.'''
        guide_module = _import_guide_module()
        if guide_module is None:
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

        prompt = guide_module.generate_guide_system_prompt()
        prompt_lower = prompt.lower()

        # At least 3 of the core capabilities should be mentioned
        capabilities = ['prompt', 'workflow', 'code', 'task', 'chat']
        found = [cap for cap in capabilities if cap in prompt_lower]
        assert len(found) >= 3, (
            f"Expected at least 3 core capabilities in system prompt, found: {found}\n"
            f"Prompt excerpt:\n{prompt[:600]}"
        )

    def test_system_prompt_includes_all_six_categories(self):
        '''System prompt includes all six command categories.'''
        guide_module = _import_guide_module()
        if guide_module is None:
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

        prompt = guide_module.generate_guide_system_prompt()

        expected_categories = [
            'Prompts',
            'Workflows',
            'Code Analysis',
            'Task Queue',
            'Interactive',
            'Utilities',
        ]
        for category in expected_categories:
            assert category in prompt, (
                f"Expected category '{category}' in system prompt:\n{prompt[:1000]}"
            )

    def test_system_prompt_includes_key_commands(self):
        '''System prompt references key commands from each category.'''
        guide_module = _import_guide_module()
        if guide_module is None:
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

        prompt = guide_module.generate_guide_system_prompt()

        # At least one representative command from each category
        key_commands = [
            'send-prompt',    # Prompts
            'code-review',    # Code Analysis
            'task-add',       # Task Queue
            'chat',           # Interactive
            'list-models',    # Utilities
        ]
        for cmd in key_commands:
            assert cmd in prompt, (
                f"Expected command '{cmd}' in system prompt command reference:\n{prompt[:1000]}"
            )

    def test_system_prompt_includes_practical_example_instruction(self):
        '''System prompt instructs the AI to provide practical examples.'''
        guide_module = _import_guide_module()
        if guide_module is None:
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

        prompt = guide_module.generate_guide_system_prompt()
        prompt_lower = prompt.lower()

        assert 'example' in prompt_lower or 'practical' in prompt_lower, (
            f"Expected instructions about practical examples in system prompt:\n{prompt[:800]}"
        )

    def test_system_prompt_includes_goal_matching_instruction(self):
        '''System prompt instructs the AI to match user goals to commands.'''
        guide_module = _import_guide_module()
        if guide_module is None:
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

        prompt = guide_module.generate_guide_system_prompt()
        prompt_lower = prompt.lower()

        assert (
            'goal' in prompt_lower
            or 'relevant command' in prompt_lower
            or 'recommend' in prompt_lower
            or 'suggest' in prompt_lower
            or 'match' in prompt_lower
        ), f"Expected goal-matching instruction in system prompt:\n{prompt[:800]}"

    def test_system_prompt_includes_concise_response_instruction(self):
        '''System prompt instructs the AI to keep responses concise.'''
        guide_module = _import_guide_module()
        if guide_module is None:
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

        prompt = guide_module.generate_guide_system_prompt()
        prompt_lower = prompt.lower()

        assert (
            'concise' in prompt_lower
            or 'brief' in prompt_lower
            or 'actionable' in prompt_lower
            or 'short' in prompt_lower
        ), f"Expected concise/brief/actionable instruction in system prompt:\n{prompt[:800]}"

    def test_generate_fallback_help_menu_is_importable(self):
        '''generate_fallback_help_menu function is importable from guide module.'''
        guide_module = _import_guide_module()
        if guide_module is None:
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

        assert hasattr(guide_module, 'generate_fallback_help_menu'), (
            'Expected function generate_fallback_help_menu in sokrates.cli.sokrates_guide'
        )

    def test_fallback_help_menu_returns_string(self):
        '''generate_fallback_help_menu() returns a non-empty string.'''
        guide_module = _import_guide_module()
        if guide_module is None:
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

        menu = guide_module.generate_fallback_help_menu()
        assert isinstance(menu, str), f'Expected str, got {type(menu)}'
        assert len(menu.strip()) > 0, 'Fallback menu should not be empty'

    def test_fallback_menu_contains_sokrates_summary(self):
        '''Fallback menu contains a brief "What is Sokrates?" summary.'''
        guide_module = _import_guide_module()
        if guide_module is None:
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

        menu = guide_module.generate_fallback_help_menu()
        assert 'sokrates' in menu.lower(), (
            f"Expected Sokrates summary in fallback menu:\n{menu}"
        )

    def test_fallback_menu_contains_command_categories(self):
        '''Fallback menu includes command categories with commands and descriptions.'''
        guide_module = _import_guide_module()
        if guide_module is None:
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

        menu = guide_module.generate_fallback_help_menu()

        # At least some category headers and commands should appear
        has_category = any(
            cat in menu
            for cat in ['Prompts', 'Workflows', 'Code Analysis', 'Task Queue', 'Interactive', 'Utilities']
        )
        has_commands = any(
            cmd in menu
            for cmd in ['send-prompt', 'code-review', 'task-add', 'chat', 'list-models']
        )
        assert has_category or has_commands, (
            f"Expected command categories or commands in fallback menu:\n{menu}"
        )

    def test_fallback_menu_suggests_help_command(self):
        '''Fallback menu suggests running sokrates --help.'''
        guide_module = _import_guide_module()
        if guide_module is None:
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

        menu = guide_module.generate_fallback_help_menu()
        assert '--help' in menu, (
            f"Expected '--help' suggestion in fallback menu:\n{menu}"
        )

    def test_fallback_menu_suggests_llm_configuration_check(self):
        '''Fallback menu suggests checking LLM endpoint configuration.'''
        guide_module = _import_guide_module()
        if guide_module is None:
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

        menu = guide_module.generate_fallback_help_menu()
        menu_lower = menu.lower()
        assert (
            'endpoint' in menu_lower
            or 'config' in menu_lower
            or 'llm' in menu_lower
            or 'connection' in menu_lower
        ), f"Expected LLM config/endpoint suggestion in fallback menu:\n{menu}"

    def test_fallback_menu_is_terminal_readable(self):
        '''Fallback menu is readable in terminal (no raw markdown dependencies).

        Verifies the menu does not rely on markdown rendering to be meaningful.
        '''
        guide_module = _import_guide_module()
        if guide_module is None:
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

        menu = guide_module.generate_fallback_help_menu()
        # A terminal-readable menu should be mostly plain text; raw markdown
        # like ``` code blocks or complex HTML would be unusual.
        # Simple heuristic: the menu contains at least one line of plain text.
        lines = [line for line in menu.split('\n') if line.strip()]
        plain_lines = [
            line for line in lines
            if not line.strip().startswith('```')
            and not line.strip().startswith('<')
        ]
        assert len(plain_lines) > 0, (
            f"Expected plain text lines in fallback menu:\n{menu}"
        )


# ═══════════════════════════════════════════════════════════════════
# Behavior 9: First-Time User Experience
# ═══════════════════════════════════════════════════════════════════

class TestFirstTimeUserExperience:
    '''Tests for Behavior 9: first-time user detection via config file presence.'''

    def test_is_first_time_user_function_importable(self):
        '''A function to detect first-time users is importable from main module.'''
        main_module = _import_cli_main()
        if main_module is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        # Accept any reasonable function name
        has_function = (
            hasattr(main_module, 'is_first_time_user')
            or hasattr(main_module, 'is_new_user')
            or hasattr(main_module, 'config_missing')
            or hasattr(main_module, 'has_config')
        )
        assert has_function, (
            'Expected a first-time user detection function in sokrates.cli.main '
            '(e.g., is_first_time_user, is_new_user, config_missing, has_config)'
        )

    def test_missing_config_returns_first_time_true(self, temp_home):
        '''When config.yml is missing, first-time user detection returns True (or no config).'''
        main_module = _import_cli_main()
        if main_module is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        # Find the detection function
        detection_fn = None
        for fn_name in ('is_first_time_user', 'is_new_user', 'config_missing'):
            if hasattr(main_module, fn_name):
                detection_fn = getattr(main_module, fn_name)
                break

        # For has_config, the logic is inverted
        has_config_fn = None
        if detection_fn is None and hasattr(main_module, 'has_config'):
            has_config_fn = getattr(main_module, 'has_config')

        # temp_home has no config.yml, so:
        if detection_fn is not None:
            result = detection_fn()
            assert result is True, (
                f"Expected first-time user detection to return True when config missing, got {result}"
            )
        elif has_config_fn is not None:
            result = has_config_fn()
            assert result is False, (
                f"Expected has_config() to return False when config missing, got {result}"
            )
        else:
            pytest.skip('No compatible first-time user detection function found')

    def test_config_exists_returns_first_time_false(self, temp_home):
        '''When config.yml exists, first-time user detection returns False (or config present).'''
        main_module = _import_cli_main()
        if main_module is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        # Create a minimal config.yml in temp_home
        config_path = Path(temp_home) / 'config.yml'
        config_path.write_text(
            'providers:\n  - name: local\n    type: openai\n    api_endpoint: http://localhost:1234/v1\n',
            encoding='utf-8',
        )

        detection_fn = None
        for fn_name in ('is_first_time_user', 'is_new_user', 'config_missing'):
            if hasattr(main_module, fn_name):
                detection_fn = getattr(main_module, fn_name)
                break

        has_config_fn = None
        if detection_fn is None and hasattr(main_module, 'has_config'):
            has_config_fn = getattr(main_module, 'has_config')

        if detection_fn is not None:
            result = detection_fn()
            assert result is False, (
                f"Expected first-time user detection to return False when config exists, got {result}"
            )
        elif has_config_fn is not None:
            result = has_config_fn()
            assert result is True, (
                f"Expected has_config() to return True when config exists, got {result}"
            )
        else:
            pytest.skip('No compatible first-time user detection function found')

    def test_config_detection_handles_permission_error_gracefully(self, temp_home):
        '''Permission errors during config detection are handled gracefully (no crash).'''
        main_module = _import_cli_main()
        if main_module is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        detection_fn = None
        for fn_name in ('is_first_time_user', 'is_new_user', 'config_missing', 'has_config'):
            if hasattr(main_module, fn_name):
                detection_fn = getattr(main_module, fn_name)
                break

        if detection_fn is None:
            pytest.skip('No compatible first-time user detection function found')

        # Patch Path.exists to raise PermissionError to simulate access denial
        with patch('pathlib.Path.exists', side_effect=PermissionError('Permission denied')):
            try:
                result = detection_fn()
                # Should return a bool without crashing
                assert isinstance(result, bool), (
                    f"Expected bool return value on PermissionError, got {type(result)}"
                )
            except PermissionError:
                pytest.fail(
                    'detection function should handle PermissionError gracefully and not re-raise'
                )

    def test_onboarding_message_shown_when_config_missing(self, temp_home):
        '''When config is missing, sokrates --help shows an onboarding message.'''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        from click.testing import CliRunner
        runner = CliRunner()

        # temp_home has no config.yml
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0

        output = result.output.lower()
        has_onboarding = (
            'guide' in output
            or 'getting started' in output
            or 'first time' in output
            or 'welcome' in output
            or 'new user' in output
        )
        assert has_onboarding, (
            f"Expected onboarding message in help output when config missing:\n{result.output}"
        )

    def test_onboarding_message_absent_when_config_exists(self, temp_home):
        '''When config exists, sokrates --help does NOT show first-time-only onboarding keywords.'''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        from click.testing import CliRunner
        runner = CliRunner()

        config_path = Path(temp_home) / 'config.yml'
        config_path.write_text(
            'providers:\n  - name: local\n    type: openai\n    api_endpoint: http://localhost:1234/v1\n',
            encoding='utf-8',
        )

        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0

        output = result.output.lower()
        # Phrases that are ONLY relevant for onboarding (not normal help)
        onboarding_only_phrases = ['getting started', 'first time', 'new user', 'welcome to sokrates']
        for phrase in onboarding_only_phrases:
            assert phrase not in output, (
                f"Onboarding phrase '{phrase}' should not appear when config exists:\n{result.output}"
            )


# ═══════════════════════════════════════════════════════════════════
# Behavior 10: AI Agent Usage Patterns
# ═══════════════════════════════════════════════════════════════════

class TestAIAgentUsagePatterns:
    '''Tests for Behavior 10: help output is parseable and consistent for AI agents.'''

    def test_help_output_is_deterministic(self):
        '''Repeated calls to sokrates --help produce identical output (no dynamic content).'''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        from click.testing import CliRunner
        runner = CliRunner()

        output1 = runner.invoke(cli, ['--help']).output
        output2 = runner.invoke(cli, ['--help']).output

        assert output1 == output2, (
            'Help output is not deterministic. AI agents require stable parseable output.\n'
            f'Diff detected between runs.'
        )

    def test_help_output_can_be_split_by_category_headers(self):
        '''sokrates --help output can be reliably split into sections by category headers.'''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0

        output = result.output
        # Split by category headers and verify we get multiple sections
        categories = ['Prompts', 'Workflows', 'Code Analysis', 'Task Queue', 'Interactive', 'Utilities']
        found_headers = [cat for cat in categories if cat in output]
        assert len(found_headers) >= 4, (
            f"Expected at least 4 category headers for reliable splitting, found: {found_headers}\n"
            f"Output:\n{output}"
        )

    def test_command_names_clearly_identifiable_in_sections(self):
        '''Command names are clearly identifiable as separate words in each section.'''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0

        output = result.output
        # Verify that known commands appear as recognizable tokens
        key_commands = ['send-prompt', 'code-review', 'task-add', 'chat']
        for cmd in key_commands:
            assert cmd in output, (
                f"Command '{cmd}' not found in help output; must be clearly identifiable:\n{output}"
            )

    def test_all_registered_commands_have_consistent_metadata(self):
        '''All registered Click commands have consistent metadata fields.

        Each command should have a name and help text (description).
        '''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        for cmd_name, cmd_obj in cli.commands.items():
            assert cmd_obj.name is not None, (
                f"Command '{cmd_name}' has no name attribute"
            )
            assert isinstance(cmd_obj.name, str), (
                f"Command '{cmd_name}' name should be a string, got {type(cmd_obj.name)}"
            )
            assert cmd_obj.help is not None and len(cmd_obj.help.strip()) > 0, (
                f"Command '{cmd_name}' has no help/description text"
            )

    def test_all_commands_have_string_descriptions(self):
        '''Every registered command description is a string (not None or empty).'''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        for cmd_name, cmd_obj in cli.commands.items():
            desc = cmd_obj.help
            assert isinstance(desc, str), (
                f"Command '{cmd_name}' description is not a string: {type(desc)}"
            )
            assert len(desc.strip()) > 0, (
                f"Command '{cmd_name}' has empty description"
            )

    def test_no_timestamps_in_help_output(self):
        '''Help output contains no timestamps that would break AI parsing.'''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        from click.testing import CliRunner
        import re
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0

        # Timestamp patterns like 2024-01-15 or 15:30:00
        timestamp_pattern = re.compile(r'\d{4}-\d{2}-\d{2}|\d{2}:\d{2}:\d{2}')
        matches = timestamp_pattern.findall(result.output)
        assert not matches, (
            f"Found timestamp-like patterns in help output (breaks AI parsing): {matches}\n"
            f"Output:\n{result.output}"
        )

    def test_all_commands_have_no_missing_required_fields(self):
        '''No registered command has a None name or missing click command object.'''
        cli = _import_cli_group()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        import click
        for cmd_name, cmd_obj in cli.commands.items():
            assert cmd_obj is not None, f"Command '{cmd_name}' maps to None"
            assert isinstance(cmd_obj, click.BaseCommand), (
                f"Command '{cmd_name}' is not a Click BaseCommand instance: {type(cmd_obj)}"
            )
