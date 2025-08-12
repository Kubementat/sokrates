import sys
import os
from pathlib import Path
import pytest

# Add the src directory to the Python path
# This allows importing sokrates modules directly
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Create a symbolic link in sys.modules to enable direct imports
# This makes 'from sokrates.utils import Utils' work the same as
# 'from src.sokrates.utils import Utils'
import src.sokrates
sys.modules['sokrates'] = src.sokrates

pytest.TESTING_MODEL = "qwen3-4b-instruct-2507-mlx"
