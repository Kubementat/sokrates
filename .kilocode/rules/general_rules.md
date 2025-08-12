# Usage of uv for project depenency management and execution
- WHEN CALLING `python` VIA THE COMMAND LINE WITH ANY SCRIPT ALWAYS USE `uv run python`
- WHEN USING COMMANDS FROM `pyproject.toml` ALWAYS EXECUTE THE COMMAND via `uv run <command>`
  - e.g.: `uv run sokrates-list-models`