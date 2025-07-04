import os
from dotenv import load_dotenv
from pathlib import Path
from .colors import Colors

"""
A class for managing configuration settings.
"""
class Config:
  DEFAULT_API_ENDPOINT = "http://localhost:1234/v1"
  DEFAULT_API_KEY = "notrequired"
  DEFAULT_MODEL = "qwen/qwen3-8b"
  
  def __init__(self, verbose=False) -> None:
    self.verbose = verbose
    self.config_path: str = f"{str(Path.home())}/.llm_tools/.env"
    if os.environ.get('LLM_TOOLS_CONFIG_FILEPATH'):
      self.config_path: str = os.environ.get('LLM_TOOLS_CONFIG_FILEPATH')
    self.load_env()
    
  def load_env(self) -> None:
      # Load environment variables from .env file
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
