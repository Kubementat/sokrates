# This script defines the `Config` class, which is responsible for managing
# application-wide configuration settings. It loads environment variables
# from a `.env` file, providing default values for API endpoints, API keys,
# and the default LLM model. This centralizes configuration management
# and allows for easy customization via environment variables.

import os
from pathlib import Path
from dotenv import load_dotenv
from .colors import Colors

class Config:
  """
  Manages configuration settings for the LLM tools application.
  Loads environment variables from a .env file and provides default values
  for various settings like API endpoint, API key, and default model.
  """
  DEFAULT_API_ENDPOINT = "http://localhost:1234/v1"
  DEFAULT_API_KEY = "notrequired"
  DEFAULT_MODEL = "qwen/qwen3-8b"
  DEFAULT_PROMPTS_DIRECTORY = Path(f"{Path(__file__).parent.resolve()}/prompts").resolve()
  
  def __init__(self, verbose=False) -> None:
    """
    Initializes the Config object.

    Args:
        verbose (bool): If True, prints basic configuration details upon loading.
    """
    self.verbose = verbose
    # Determine the configuration file path. Prioritize LLM_TOOLS_CONFIG_FILEPATH environment variable.
    self.config_path: str = f"{str(Path.home())}/.llm_tools/.env"
    if os.environ.get('LLM_TOOLS_CONFIG_FILEPATH'):
      self.config_path: str = os.environ.get('LLM_TOOLS_CONFIG_FILEPATH')
    self.load_env()
    
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

      if self.verbose:
        print(f"{Colors.GREEN}{Colors.BOLD}Basic Configuration:{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD}API_ENDPOINT: {self.api_endpoint}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD}DEFAULT_MODEL: {self.default_model}{Colors.RESET}")
