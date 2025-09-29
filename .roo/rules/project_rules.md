# Project specific rules for sokrates
## Commands
- Build: `uv sync --all-extras`
- Lint: `uv run ruff check src/ tests/`
- Test Single File: `uv run pytest tests/{filename}.py`
- Run Specific Test: `uv run pytest tests/{filename}.py::{test_function}`

## Code Style
- PEP8 compliant with 4-space indents
- Type hints required for all public functions
- Imports sorted alphabetically (stdlib > third-party > local)
- Use f-strings and type annotations consistently
- Avoid bare excepts; handle specific exceptions
- Error messages include context and actionable info
- No trailing commas in function calls/definitions