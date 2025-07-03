import os
from dotenv import load_dotenv
from pathlib import Path
from .colors import Colors

"""
A class for managing configuration settings.
"""
class Config:
  def __init__(self) -> None:
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
        self.api_endpoint = "http://localhost:1234/v1"
      if not self.api_key:
        self.api_key = "notrequired"
      if not self.default_model:
        self.default_model = "qwen/qwen3-8b"
      
      print(f"{Colors.GREEN}{Colors.BOLD}Basic Configuration:{Colors.RESET}")
      print(f"{Colors.BLUE}{Colors.BOLD}API_ENDPOINT: {self.api_endpoint}{Colors.RESET}")
      print(f"{Colors.BLUE}{Colors.BOLD}DEFAULT_MODEL: {self.default_model}{Colors.RESET}")
