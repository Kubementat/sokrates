# This script defines the `Config` class, which is responsible for managing
# application-wide configuration settings. It loads environment variables
# from a `config.yml` file, providing default values for API endpoints, API keys,
# and the default LLM model. This centralizes configuration management
# and allows for easy customization via environment variables.

import os
import logging
from typing import Any, MutableMapping
from pathlib import Path

from mergedeep import merge

from .constants import Constants
from .file_helper import FileHelper

class Config:
  """
  Manages configuration settings for the LLM tools application.
  Can load configuration from a yaml file.
  """

  DEFAULT_CONFIGURATION = {
    "home_path": Constants.DEFAULT_HOME_PATH,
    "prompts_directory": Constants.DEFAULT_PROMPTS_DIRECTORY,
    "default_provider": Constants.DEFAULT_PROVIDER_NAME,
    "providers": [
      # {
      #   "name": Constants.DEFAULT_PROVIDER_NAME,
      #   "type": Constants.DEFAULT_PROVIDER_TYPE,
      #   "api_endpoint": Constants.DEFAULT_API_ENDPOINT,
      #   "api_key": Constants.DEFAULT_API_KEY,
      #   "default_model": Constants.DEFAULT_MODEL,
      #   "default_temperature": Constants.DEFAULT_MODEL_TEMPERATURE
      # }
    ],
    "daemon": {
      "processing_interval": Constants.DEFAULT_DAEMON_PROCESSING_INTERVAL,
      "file_watcher": {
        "enabled": False
      }
    }
  }

  REQUIRED_CONFIG_KEYS = [
    "home_path",
    "config_path",
    "logs_path",
    "database_path",
    "prompts_directory",
    "default_provider",
    "daemon.processing_interval",
    "daemon.logfile_path",
    "daemon.file_watcher.enabled"
  ]
  
  def __init__(self) -> None:
    """
    Initializes the Config object.
    
    Sets up the initial configuration using defaults, and configures
    basic paths needed for other operations like loading from files or setting up directories.
    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.config = self.DEFAULT_CONFIGURATION

    # Set up basic paths first (needed for other config)
    self._configure_basic_paths()

  def _configure_basic_paths(self) -> None:
    """
    Sets up basic path configuration including home, config, logs, and database paths.
    
    Determines the configuration file path (prioritizing SOKRATES_HOME_PATH environment variable),
    and sets up all required directory paths for the application's operation.
    """
    # Determine the configuration file path. Prioritize SOKRATES_HOME_PATH environment variable.
    env_home_path = os.environ.get('SOKRATES_HOME_PATH', None)
    if env_home_path:
      self.config["home_path"] = Path(env_home_path)

    # config filepath
    self.config['config_path'] = (self.get('home_path') / 'config.yml').resolve()

    # log paths
    self.config['logs_path'] = (self.get('home_path') / 'logs').resolve()
    self.config['daemon']['logfile_path'] = (self.get('logs_path') / 'daemon.log').resolve()

    # database path
    self.config['database_path'] = (self.get('home_path') / 'database.sqlite').resolve()
    
  def _setup_directories(self) -> None:
    """
    Creates the necessary directory structure for the application.
    
    Ensures that the main sokrates home directory and logs directory exist,
    creating them if they don't already exist.
    
    Returns:
        None
        
    Raises:
        RuntimeError: If creation of directories fails due to permissions or other OS errors
    """
    home_path = self.get('home_path')
    logs_path = self.get('logs_path')
    self.logger.info(f"Creating sokrates home path: {home_path}")

    try:
      Path(home_path).mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError) as e:
      raise RuntimeError(f"Failed to create sokrates home directory at `{home_path}`: {e}")
    
    self.logger.info(f"Creating sokrates logs path at: {logs_path}")
    
    try:
      Path(logs_path).mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError) as e:
      raise RuntimeError(f"Failed to create sokrates logs directory at `{logs_path}`: {e}")

  def load_from_file(self, config_filepath: str | Path) -> None:
    """
    Load configuration from a YAML file and initialize all values.
    
    Reads a YAML configuration file, merges it with the default configuration,
    validates the merged result, and sets up required directories.
    
    Args:
        config_filepath: Path to the YAML configuration file
        
    Returns:
        None
        
    Raises:
        FileNotFoundError: If the specified configuration file does not exist
        yaml.YAMLError: If the YAML file is malformed
    """
    config_dict = FileHelper.read_yaml_file(file_path=Path(config_filepath))
    self.config = self._deep_merge_config(first=self.config, second=config_dict)
    self.validate()
    self._setup_directories()

  def load_from_dict(self, config_dict: dict[str, Any]) -> None:
    """
    Load configuration from a dictionary and initialize all values.
    
    Merges the provided configuration dictionary with the default configuration,
    validates the merged result, and sets up required directories.
    
    Args:
        config_dict: Dictionary containing configuration values
        
    Returns:
        None
    """
    self.config = self._deep_merge_config(first=self.config, second=config_dict)
    self.validate()
    self._setup_directories()

  def validate(self) -> None:
    """
    Validates the config parameters in the config object.
    
    Checks that all required configuration keys are present and have non-None values.
    If any required key is missing or None, a ValueError is raised.
    
    Returns:
        None
        
    Raises:
        ValueError: If any required configuration key is not set
    """
    for key in self.REQUIRED_CONFIG_KEYS:
      val = self.get(key)
      if val == None:
        raise ValueError(f"The configuration setting: {key} is not configured!")

  def get(self, key_path: str) -> Any:
    """
    Returns a configuration value under the provided key_path.
    
    Retrieves a configuration value by traversing the configuration dictionary 
    using the key path. The key path is expected to be a string with components 
    separated by dots (.).
    
    Args:
        key_path: Path to the configuration value, e.g., "daemon.processing_interval"
        
    Returns:
        The configuration value if found
        
    Raises:
        ValueError: If the key path is invalid or the value cannot be found
    """
    if not key_path:
      raise ValueError(f"Configuration key path is invalid: {key_path}")
    
    key_path_array = key_path.replace(" ", "").split('.')
    value = self.config

    not_found_error_message = f"Could not find a configuration value under the key: {key_path}"

    try:
      for key in key_path_array:
        value = value.get(key, None)
    except:
      raise ValueError(not_found_error_message)

    if value == None:
      raise ValueError(not_found_error_message)
    return value
  
  def get_default_provider(self) -> dict:
    """
    Returns the provider dict that is configured as default provider.
    
    Retrieves the configuration for the default provider by name.
    Returns None if no provider with the configured name exists.
    
    Returns:
        The provider configuration dictionary or None if not found
    """
    default_provider_name = self.config['default_provider']
    prov = self.get_provider(default_provider_name)

    if not prov:
      raise ValueError("Could not find configuration for the default provider!")
    return prov

  def get_provider(self, provider_name: str) -> dict:
    """
    Returns the configuration dict for the provider with the provided name.
    
    Searches through the configured providers and returns the dictionary 
    for the provider matching the given name. If no matching provider is found,
    it returns None.
    
    Args:
        provider_name: The name of the provider to retrieve
        
    Returns:
        The provider configuration dictionary or None if not found
    """
    providers = self.config['providers']
    provider = next(
    (d for d in providers if d.get("name") == provider_name),
      None
    )
    if not provider:
      raise ValueError(f"Could not find configuration for provider: {provider_name}")
    return provider

  def _deep_merge_config(self, first: MutableMapping, second: MutableMapping) -> MutableMapping:
    """
    Recursively merge two config dicts.
    Values from `second` override those in `first`.
    """
    return merge(first, second)
