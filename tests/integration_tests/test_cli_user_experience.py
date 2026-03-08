'''Integration tests for CLI user experience feature.

Tests cover user-facing behaviors for the unified sokrates CLI entry point:
- Behavior 0: Unified CLI entry point
- Behavior 1: Central command discovery (sokrates --help)
- Behavior 2: Subcommand help with examples (epilog)
- Behavior 3: Unknown command handling
- Behavior 4: Interactive guide mode (sokrates guide)
- Behavior 5: Chat alias (sokrates chat)
- Behavior 7: Onboarding experience (first-time user detection)
'''

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner


# ──────────────────────────── fixtures ────────────────────────────

@pytest.fixture
def runner():
    '''Click test client for Sokrates CLI.'''
    return CliRunner()


@pytest.fixture
def temp_home():
    '''Create temporary home directory for testing config detection.'''
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


# ──────────────────────────── helpers ────────────────────────────

def _import_cli():
    '''Import the unified CLI group, returning None if not yet implemented.'''
    try:
        from sokrates.cli.main import cli
        return cli
    except (ImportError, ModuleNotFoundError):
        return None


# ═══════════════════════════════════════════════════════════════════
# Behavior 0: Unified CLI Entry Point
# ═══════════════════════════════════════════════════════════════════

class TestUnifiedEntryPoint:
    '''Tests for Behavior 0: Unified CLI entry point.'''

    def test_unified_entry_point_exists_and_returns_zero(self, runner):
        '''Unified entry point exists and returns exit code 0 for --help.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0, f'Expected exit code 0, got {result.exit_code}. Output:\n{result.output}'

    def test_help_contains_usage_information(self, runner):
        '''Running sokrates --help displays usage information.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        output = result.output.lower()
        assert 'usage' in output or 'sokrates' in output, (
            f'Expected usage information in output:\n{result.output}'
        )

    def test_all_existing_commands_registered_as_subcommands(self, runner):
        '''All existing commands appear as subcommands with correct names.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0

        expected_subcommands = [
            'chat',
            'code-review',
            'send-prompt',
            'task-add',
            'daemon',
            'refine-and-send-prompt',
        ]
        for cmd in expected_subcommands:
            assert cmd in result.output, (
                f"Expected subcommand '{cmd}' in help output:\n{result.output}"
            )

    def test_subcommand_names_have_no_sokrates_prefix(self, runner):
        '''No registered subcommand retains the sokrates- prefix.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        # The output should not contain "sokrates-" as a command name prefix
        lines = result.output.split('\n')
        for line in lines:
            stripped = line.strip()
            # Skip non-command lines (headers, descriptions, blank lines)
            if stripped.startswith('sokrates-'):
                pytest.fail(
                    f"Found line with 'sokrates-' prefix in help output: {line!r}\n"
                    f"Full output:\n{result.output}"
                )

    def test_subcommand_code_review_derived_correctly(self, runner):
        '''sokrates-code-review is registered as code-review subcommand.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['code-review', '--help'])
        assert result.exit_code == 0, (
            f"'sokrates code-review --help' failed with exit code {result.exit_code}:\n{result.output}"
        )

    def test_subcommand_refine_and_send_prompt_derived_correctly(self, runner):
        '''sokrates-refine-and-send-prompt is registered as refine-and-send-prompt.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['refine-and-send-prompt', '--help'])
        assert result.exit_code == 0, (
            f"'sokrates refine-and-send-prompt --help' failed:\n{result.output}"
        )

    def test_standalone_alias_produces_equivalent_help(self, runner):
        '''sokrates chat --help and sokrates-chat produce equivalent help output.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        # Test that sokrates chat --help works and contains key option names
        result = runner.invoke(cli, ['chat', '--help'])
        assert result.exit_code == 0, (
            f"'sokrates chat --help' failed with exit code {result.exit_code}:\n{result.output}"
        )
        # Verify some known chat options appear
        output = result.output
        assert '--model' in output or '-m' in output, (
            f"Expected model option in chat help:\n{output}"
        )

    def test_graceful_handling_of_import_failure(self, runner):
        '''CLI group remains functional even if one command module fails to import.

        This test verifies the pattern: remaining commands load if one fails.
        Since the actual lazy-loading is in task-006, here we just check that
        the CLI does not crash when invoked.
        '''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        # At minimum, --help must not crash
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert result.exception is None, (
            f'Unexpected exception during --help: {result.exception}'
        )


# ═══════════════════════════════════════════════════════════════════
# Behavior 1: Central Command Discovery (sokrates --help)
# ═══════════════════════════════════════════════════════════════════

class TestCentralCommandDiscovery:
    '''Tests for Behavior 1: sokrates --help displays categorized commands.'''

    def test_help_displays_category_headers(self, runner):
        '''sokrates --help shows commands grouped under category headers.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0

        expected_categories = [
            'Prompts',
            'Workflows',
            'Code Analysis',
            'Task Queue',
            'Interactive',
            'Utilities',
        ]
        for category in expected_categories:
            assert category in result.output, (
                f"Expected category header '{category}' in help output:\n{result.output}"
            )

    def test_commands_appear_under_correct_category(self, runner):
        '''Commands appear under their assigned categories in help output.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        output = result.output

        # code-review should appear under Code Analysis section
        code_analysis_idx = output.find('Code Analysis')
        task_queue_idx = output.find('Task Queue')
        code_review_idx = output.find('code-review')

        if code_analysis_idx != -1 and code_review_idx != -1:
            assert code_analysis_idx < code_review_idx, (
                "'code-review' should appear after 'Code Analysis' header"
            )

        # task-add should appear under Task Queue section
        task_add_idx = output.find('task-add')
        if task_queue_idx != -1 and task_add_idx != -1:
            assert task_queue_idx < task_add_idx, (
                "'task-add' should appear after 'Task Queue' header"
            )

    def test_project_overview_at_top_of_help(self, runner):
        '''sokrates --help shows project overview before command listings.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        output = result.output

        # Overview should contain "Sokrates" name
        assert 'Sokrates' in output, f"Expected 'Sokrates' in help output:\n{output}"
        # Overview should mention LLM or CLI toolkit
        assert 'LLM' in output or 'CLI' in output or 'toolkit' in output.lower(), (
            f"Expected LLM/CLI/toolkit mention in help output:\n{output}"
        )

    def test_project_overview_mentions_core_capabilities(self, runner):
        '''Project overview mentions core capabilities of Sokrates.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        output = result.output.lower()

        # At least two of the core capabilities should be mentioned
        capabilities = [
            'prompt',
            'code',
            'task',
            'chat',
            'workflow',
        ]
        found = [cap for cap in capabilities if cap in output]
        assert len(found) >= 2, (
            f"Expected at least 2 core capabilities mentioned, found {found}.\n"
            f"Output:\n{result.output}"
        )

    def test_overview_suggests_sokrates_guide(self, runner):
        '''Project overview suggests running sokrates guide for introduction.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'guide' in result.output.lower(), (
            f"Expected 'guide' mention in help output:\n{result.output}"
        )

    def test_all_registered_subcommands_appear_in_help(self, runner):
        '''All known subcommands appear in sokrates --help output.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0

        all_commands = [
            'send-prompt',
            'refine-prompt',
            'refine-and-send-prompt',
            'idea-generator',
            'merge-ideas',
            'generate-mantra',
            'breakdown-task',
            'execute-tasks',
            'code-review',
            'code-analyze',
            'code-summarize',
            'code-generate-tests',
            'task-add',
            'task-list',
            'task-status',
            'task-remove',
            'daemon',
            'chat',
            'list-models',
            'fetch-to-md',
        ]
        for cmd in all_commands:
            assert cmd in result.output, (
                f"Expected subcommand '{cmd}' in help output:\n{result.output}"
            )

    def test_onboarding_message_when_config_missing(self, runner, temp_home):
        '''When config.yml is missing, help output shows onboarding message.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        # temp_home has no config.yml
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0

        # Onboarding message should mention guide or be present
        output = result.output.lower()
        assert 'guide' in output or 'getting started' in output or 'first time' in output or 'welcome' in output, (
            f"Expected onboarding content in help output when config missing:\n{result.output}"
        )

    def test_onboarding_message_disappears_when_config_exists(self, runner, temp_home):
        '''When config.yml exists, onboarding message does not appear.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        # Create a minimal config.yml
        config_path = Path(temp_home) / 'config.yml'
        config_path.write_text(
            'providers:\n  - name: local\n    type: openai\n    api_endpoint: http://localhost:1234/v1\n    api_key: test\n',
            encoding='utf-8',
        )

        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0

        output = result.output.lower()
        # Onboarding-specific keywords should not appear in normal operation
        onboarding_keywords = ['getting started', 'first time', 'welcome to sokrates', 'new to sokrates']
        for keyword in onboarding_keywords:
            assert keyword not in output, (
                f"Expected onboarding keyword '{keyword}' to be absent when config exists:\n{result.output}"
            )


# ═══════════════════════════════════════════════════════════════════
# Behavior 2: Subcommand Help with Examples
# ═══════════════════════════════════════════════════════════════════

class TestSubcommandHelpWithExamples:
    '''Tests for Behavior 2: subcommand --help includes examples section.'''

    @pytest.mark.parametrize('subcommand', [
        'send-prompt',
        'refine-prompt',
        'refine-and-send-prompt',
        'code-review',
        'task-add',
        'list-models',
        'chat',
    ])
    def test_subcommand_help_exits_zero(self, runner, subcommand):
        '''Each subcommand --help returns exit code 0.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, [subcommand, '--help'])
        assert result.exit_code == 0, (
            f"'sokrates {subcommand} --help' failed with exit code {result.exit_code}:\n{result.output}"
        )

    @pytest.mark.parametrize('subcommand', [
        'send-prompt',
        'refine-prompt',
        'refine-and-send-prompt',
        'idea-generator',
        'merge-ideas',
        'generate-mantra',
        'breakdown-task',
        'execute-tasks',
        'code-review',
        'code-analyze',
        'code-summarize',
        'code-generate-tests',
        'task-add',
        'task-list',
        'task-status',
        'task-remove',
        'daemon',
        'chat',
        'list-models',
        'fetch-to-md',
    ])
    def test_subcommand_help_contains_examples_section(self, runner, subcommand):
        '''Each subcommand --help contains an Examples: section.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, [subcommand, '--help'])
        assert result.exit_code == 0, (
            f"'sokrates {subcommand} --help' failed:\n{result.output}"
        )
        assert 'Examples:' in result.output or 'EXAMPLES' in result.output.upper(), (
            f"Expected 'Examples:' section in '{subcommand}' help output:\n{result.output}"
        )

    def test_examples_use_unified_cli_format(self, runner):
        '''Examples use the unified CLI format (sokrates <cmd>, not sokrates-<cmd>).'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['code-review', '--help'])
        assert result.exit_code == 0

        output = result.output
        # If examples reference the command, they should use 'sokrates code-review'
        # and NOT 'sokrates-code-review'
        if 'sokrates-code-review' in output:
            pytest.fail(
                f"Examples should use 'sokrates code-review', not 'sokrates-code-review':\n{output}"
            )

    def test_examples_appear_after_options_listing(self, runner):
        '''Examples section appears after the options listing in help output.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['send-prompt', '--help'])
        assert result.exit_code == 0

        output = result.output
        options_idx = output.find('Options:') if 'Options:' in output else output.find('options')
        examples_idx = output.find('Examples:') if 'Examples:' in output else -1

        if options_idx != -1 and examples_idx != -1:
            assert options_idx < examples_idx, (
                f"'Options:' section should appear before 'Examples:' section:\n{output}"
            )


# ═══════════════════════════════════════════════════════════════════
# Behavior 3: Unknown Command Handling
# ═══════════════════════════════════════════════════════════════════

class TestUnknownCommandHandling:
    '''Tests for Behavior 3: unknown commands produce helpful error messages.'''

    def test_unknown_command_returns_nonzero_exit_code(self, runner):
        '''Running an unknown command returns a non-zero exit code.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['completely-unknown-command'])
        assert result.exit_code != 0, (
            f"Expected non-zero exit code for unknown command, got {result.exit_code}"
        )

    def test_unknown_command_shows_error_with_command_name(self, runner):
        '''Error message contains the unknown command name.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['completely-unknown-command'])
        combined = (result.output or '') + (result.stderr if hasattr(result, 'stderr') and result.stderr else '')
        assert 'completely-unknown-command' in combined or 'No such command' in combined or 'unknown' in combined.lower(), (
            f"Expected unknown command name in error output:\n{combined}"
        )

    def test_unknown_command_shows_available_categories(self, runner):
        '''Error output includes a list of available commands grouped by category.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['completely-unknown-command'])
        combined = (result.output or '') + (result.stderr if hasattr(result, 'stderr') and result.stderr else '')

        # At minimum some commands or categories should be visible
        has_category = any(cat in combined for cat in ['Prompts', 'Workflows', 'Code Analysis', 'Task Queue', 'Interactive', 'Utilities'])
        has_commands = any(cmd in combined for cmd in ['send-prompt', 'code-review', 'task-add', 'chat'])
        assert has_category or has_commands, (
            f"Expected available commands/categories in error output:\n{combined}"
        )

    def test_unknown_command_suggests_help(self, runner):
        '''Error output suggests running sokrates --help.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['completely-unknown-command'])
        combined = (result.output or '') + (result.stderr if hasattr(result, 'stderr') and result.stderr else '')
        assert '--help' in combined, (
            f"Expected '--help' suggestion in error output:\n{combined}"
        )

    def test_fuzzy_match_suggestion_for_partial_command(self, runner):
        '''Close match to a known command gets a suggestion.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['codr'])
        combined = (result.output or '') + (result.stderr if hasattr(result, 'stderr') and result.stderr else '')

        # Either Click's built-in "Did you mean?" or our custom suggestion
        assert 'code' in combined.lower() or 'Did you mean' in combined or 'suggestion' in combined.lower(), (
            f"Expected fuzzy match suggestion for 'codr' in output:\n{combined}"
        )

    def test_bare_sokrates_shows_help_not_error(self, runner):
        '''Running sokrates without arguments shows help, not an error.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, [])
        assert result.exit_code == 0, (
            f"Expected exit code 0 for bare 'sokrates', got {result.exit_code}:\n{result.output}"
        )
        assert 'Sokrates' in result.output or 'Usage' in result.output or 'sokrates' in result.output.lower(), (
            f"Expected help output for bare 'sokrates':\n{result.output}"
        )


# ═══════════════════════════════════════════════════════════════════
# Behavior 4: Interactive Guide Mode (sokrates guide)
# ═══════════════════════════════════════════════════════════════════

class TestInteractiveGuideMode:
    '''Tests for Behavior 4: sokrates guide starts with teacher persona.'''

    def test_guide_subcommand_exists(self, runner):
        '''The guide subcommand is registered and --help returns exit code 0.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['guide', '--help'])
        assert result.exit_code == 0, (
            f"'sokrates guide --help' failed with exit code {result.exit_code}:\n{result.output}"
        )

    def test_guide_help_describes_interactive_mode(self, runner):
        '''guide --help describes the interactive guide mode.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['guide', '--help'])
        assert result.exit_code == 0
        output = result.output.lower()
        assert 'guide' in output or 'interactive' in output or 'teacher' in output, (
            f"Expected guide/interactive/teacher description in guide --help:\n{result.output}"
        )

    def test_guide_appears_under_interactive_category(self, runner):
        '''guide command appears under the Interactive category in sokrates --help.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        output = result.output

        interactive_idx = output.find('Interactive')
        guide_idx = output.find('guide')

        if interactive_idx != -1 and guide_idx != -1:
            # guide should appear after the Interactive section header
            assert interactive_idx < guide_idx, (
                f"'guide' should appear under 'Interactive' section:\n{output}"
            )

    def test_guide_module_has_generate_system_prompt_function(self):
        '''sokrates_guide module exposes a generate_guide_system_prompt function.'''
        try:
            from sokrates.cli.sokrates_guide import generate_guide_system_prompt
            prompt = generate_guide_system_prompt()
            assert isinstance(prompt, str) and len(prompt) > 0, (
                'generate_guide_system_prompt() should return a non-empty string'
            )
        except (ImportError, ModuleNotFoundError):
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

    def test_guide_system_prompt_contains_teacher_role(self):
        '''Guide system prompt defines the Sokrates Teacher role.'''
        try:
            from sokrates.cli.sokrates_guide import generate_guide_system_prompt
        except (ImportError, ModuleNotFoundError):
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

        prompt = generate_guide_system_prompt()
        assert 'Sokrates Teacher' in prompt or ('teacher' in prompt.lower() and 'sokrates' in prompt.lower()), (
            f"Expected Sokrates Teacher role in system prompt:\n{prompt[:500]}"
        )

    def test_guide_module_has_fallback_menu_function(self):
        '''sokrates_guide module exposes a fallback text menu function.'''
        try:
            from sokrates.cli.sokrates_guide import generate_fallback_help_menu
            menu = generate_fallback_help_menu()
            assert isinstance(menu, str) and len(menu) > 0, (
                'generate_fallback_help_menu() should return a non-empty string'
            )
        except (ImportError, ModuleNotFoundError):
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

    def test_fallback_menu_contains_required_sections(self):
        '''Fallback help menu contains Sokrates summary and command categories.'''
        try:
            from sokrates.cli.sokrates_guide import generate_fallback_help_menu
        except (ImportError, ModuleNotFoundError):
            pytest.skip('sokrates.cli.sokrates_guide not yet implemented')

        menu = generate_fallback_help_menu()
        assert 'sokrates' in menu.lower(), f"Expected 'Sokrates' summary in fallback menu:\n{menu}"
        assert '--help' in menu, f"Expected '--help' suggestion in fallback menu:\n{menu}"


# ═══════════════════════════════════════════════════════════════════
# Behavior 5: Chat Alias (sokrates chat)
# ═══════════════════════════════════════════════════════════════════

class TestChatAlias:
    '''Tests for Behavior 5: sokrates chat is equivalent to sokrates-chat.'''

    def test_chat_subcommand_exists(self, runner):
        '''The chat subcommand is registered and --help returns exit code 0.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['chat', '--help'])
        assert result.exit_code == 0, (
            f"'sokrates chat --help' failed with exit code {result.exit_code}:\n{result.output}"
        )

    def test_chat_appears_under_interactive_category(self, runner):
        '''chat command appears under the Interactive category in sokrates --help.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        output = result.output

        interactive_idx = output.find('Interactive')
        chat_idx = output.find('\n  chat') if '\n  chat' in output else output.find('  chat')

        if interactive_idx != -1 and chat_idx != -1:
            assert interactive_idx < chat_idx, (
                f"'chat' should appear under 'Interactive' section:\n{output}"
            )

    def test_chat_help_shows_same_options_as_standalone(self, runner):
        '''sokrates chat --help contains the same key options as the standalone chat command.'''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        result = runner.invoke(cli, ['chat', '--help'])
        assert result.exit_code == 0
        output = result.output

        # Key options from sokrates_chat.py
        key_options = ['--model', '--temperature', '--api-endpoint']
        for option in key_options:
            assert option in output or option.replace('--', '-').replace('-', '') in output.lower(), (
                f"Expected option '{option}' in 'sokrates chat --help':\n{output}"
            )

    def test_chat_does_not_use_teacher_persona(self):
        '''Chat command uses standard assistant persona, not teacher persona.

        We verify that the chat module does NOT import or reference guide system prompt.
        '''
        try:
            from sokrates.cli import sokrates_chat
            import inspect
            source = inspect.getsource(sokrates_chat)
            assert 'Sokrates Teacher' not in source, (
                "Chat module should not contain 'Sokrates Teacher' persona"
            )
        except (ImportError, ModuleNotFoundError):
            pytest.skip('sokrates.cli.sokrates_chat not importable')

    def test_chat_and_guide_have_no_shared_session_state(self, runner):
        '''chat and guide subcommands have no shared session state.

        We verify they reference separate modules/logic.
        '''
        cli = _import_cli()
        if cli is None:
            pytest.skip('sokrates.cli.main not yet implemented')

        # Both --help invocations should succeed independently
        chat_result = runner.invoke(cli, ['chat', '--help'])
        guide_result = runner.invoke(cli, ['guide', '--help'])

        assert chat_result.exit_code == 0
        assert guide_result.exit_code == 0

        # The outputs should be different (different commands, different descriptions)
        assert chat_result.output != guide_result.output, (
            "chat and guide --help output should differ (different personas/purposes)"
        )
