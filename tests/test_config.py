"""
Test suite for the Config class.

This module contains unit tests for the Config class which manages application 
configuration settings. The tests cover singleton behavior, environment variable
loading, directory initialization, and configuration value retrieval.
"""

import os
from unittest.mock import patch
import pytest

from sokrates import Config
        
class TestConfig:
    """Test cases for the Config class."""

    def test_config_initialization_with_defaults(self, tmp_path):
        """Test Config initialization with default values."""
        # Create a temporary directory for testing
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        os.environ['SOKRATES_HOME_PATH'] = str(home_dir / '.sokrates')
        
        config = Config()
        
        # Check that default paths are set correctly
        assert str(config.get('home_path')) == str(home_dir / ".sokrates")
        assert str(config.get('config_path')) == str(home_dir / ".sokrates" / "config.yml")
        assert str(config.get('logs_path')) == str(home_dir / ".sokrates" / "logs")
        assert str(config.get('daemon/logfile_path')) == str(home_dir / ".sokrates" / "logs" / "daemon.log")
        assert str(config.get('database_path')) == str(home_dir / ".sokrates" / "database.sqlite")