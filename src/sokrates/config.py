# This script defines the `Config` class, which is responsible for managing
# application-wide configuration settings. It loads environment variables
# from a `.env` file, providing default values for API endpoints, API keys,
# and the default LLM model. This centralizes configuration management
# and allows for easy customization via environment variables.

import os
from pathlib import Path
from dotenv import load_dotenv
from .colors import Colors
from datetime import datetime

class Config:
  """
  Manages configuration settings for the LLM tools application.
  Loads environment variables from a .env file and provides default values
  for various settings like API endpoint, API key, and default model.
  """
  
  _instance = None  # Class variable to hold the single instance

  def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls)
            # Initialize your config here, for example:
            cls._instance.settings = {}
        return cls._instance
  
  DEFAULT_API_ENDPOINT = "http://localhost:1234/v1"
  DEFAULT_API_KEY = "notrequired"
  DEFAULT_MODEL = "qwen/qwen3-8b"
  DEFAULT_PROMPTS_DIRECTORY = Path(f"{Path(__file__).parent.resolve()}/prompts").resolve()
  DEFAULT_TASK_QUEUE_DAEMON_PROCESSING_INTERVAL = 15
  
  def __init__(self, verbose=False) -> None:
    """
    Initializes the Config object.

    Args:
        verbose (bool): If True, prints basic configuration details upon loading.
    """
    self.verbose = verbose
    # Determine the configuration file path. Prioritize SOKRATES_CONFIG_FILEPATH environment variable.
    self.home_path: str = f"{str(Path.home())}/.sokrates"
    self.config_path: str = f"{self.home_path}/.env"
    self.logs_path: str = f"{self.home_path}/logs"
    self.daemon_logfile_path: str = f"{self.logs_path}/daemon.log"
    self.task_queue_daemon_processing_interval = self.DEFAULT_TASK_QUEUE_DAEMON_PROCESSING_INTERVAL
    self.database_path: str = f"{self.home_path}/sokrates_database.sqlite"
    self.config_path: str = os.environ.get('SOKRATES_CONFIG_FILEPATH', self.config_path)
    if os.environ.get('SOKRATES_DATABASE_PATH'):
      self.database_path: str = os.environ.get('SOKRATES_DATABASE_PATH')
    if os.environ.get('SOKRATES_TASK_QUEUE_DAEMON_LOGFILE_PATH'):
      self.daemon_logfile_path: str = os.environ.get('SOKRATES_TASK_QUEUE_DAEMON_LOGFILE_PATH')      
    self.load_env()
    self.initialize_directories()
    self.print_configuration()
    
  def print_configuration(self):
      print(f"{Colors.GREEN}{Colors.BOLD}### Basic Configuration ###{Colors.RESET}")
      print(f"{Colors.BLUE}{Colors.BOLD} - SOKRATES_HOME_PATH: {self.home_path}{Colors.RESET}")
      print(f"{Colors.BLUE}{Colors.BOLD} - SOKRATES_API_ENDPOINT: {self.api_endpoint}{Colors.RESET}")
      print(f"{Colors.BLUE}{Colors.BOLD} - SOKRATES_DEFAULT_MODEL: {self.default_model}{Colors.RESET}")
      print(f"{Colors.BLUE}{Colors.BOLD} - SOKRATES_CONFIG_FILEPATH: {self.config_path}{Colors.RESET}")
      print(f"{Colors.BLUE}{Colors.BOLD} - SOKRATES_DATABASE_PATH: {self.database_path}{Colors.RESET}")
      print(f"{Colors.BLUE}{Colors.BOLD} - SOKRATES_DAEMON_LOGFILE_PATH: {self.daemon_logfile_path}{Colors.RESET}")
  
  def load_env(self) -> None:
      """
      Loads environment variables from the specified .env file.
      Sets API endpoint, API key, and default model, applying defaults if not found.
      """
      load_dotenv(self.config_path)
      self.api_endpoint: str | None = os.environ.get('API_ENDPOINT')
      self.api_key: str | None = os.environ.get('API_KEY')
      self.default_model: str | None = os.environ.get('DEFAULT_MODEL')
      
      if not self.api_endpoint:
        self.api_endpoint = self.DEFAULT_API_ENDPOINT
      if not self.api_key:
        self.api_key = self.DEFAULT_API_KEY
      if not self.default_model:
        self.default_model = self.DEFAULT_MODEL
  
  def initialize_directories(self):
    print(f"Creating sokrates home path: {self.home_path}")
    Path(self.home_path).mkdir(parents=True, exist_ok=True)
    print(f"Creating sokrates logs path: {self.logs_path}")
    Path(self.logs_path).mkdir(parents=True, exist_ok=True)
  
  @staticmethod
  def _get_local_member_value(key):
    if key == 'api_endpoint':
      return Config._instance.api_endpoint 
    if key == 'api_key':
      return Config._instance.api_endpoint 
    if key == 'default_model':
      return Config._instance.default_model
    if key == 'database_path':
      return Config._instance.database_path
    if key == 'task_queue_daemon_logfile_path':
      return Config._instance.daemon_logfile_path
    return None
  
  @staticmethod
  def get(key, default_value=None):
    lval = Config._get_local_member_value(key)
    if lval:
      return lval
    return os.environ.get(key, default_value)
  
  @staticmethod
  def create_and_return_task_execution_directory(output_directory=None):
    """
    Creates and returns the target directory for task results.

    Args:
        output_directory (Path, optional): Path to custom output directory.
            If provided, creates this directory. If None, uses default path in $HOME/.sokrates/tasks/results/YYYY-MM-DD_HH-mm .

    Returns:
        Path: Path object pointing to the created directory

    Raises:
        FileExistsError: If the specified output directory already exists
    """
    if output_directory:
        Path(output_directory).mkdir(parents=True, exist_ok=False)
        return output_directory

    
    # use default if not specified
    now = datetime.now()
    home_dir = Path.home()
    
    # Format the directory name as 'YYYY-MM-DD_HH-MM'
    directory_name = now.strftime("%Y-%m-%d_%H-%M")
    
    default_task_result_parent_dir = home_dir / ".sokrates" / "tasks" / "results"
    target_dir = Path(default_task_result_parent_dir) / directory_name
    Path(target_dir).mkdir(parents=True, exist_ok=False)
    
    return target_dir