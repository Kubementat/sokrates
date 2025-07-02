import os
from dotenv import load_dotenv
from pathlib import Path
from .colors import Colors

class Config:
  def __init__(self):
    self.config_path = f"{str(Path.home())}/.llm_tools/.env"
    if os.environ.get('LLM_TOOLS_CONFIG_FILEPATH'):
      self.config_path = os.environ.get('LLM_TOOLS_CONFIG_FILEPATH')
    self.load_env()
    
  def load_env(self):
      # Load environment variables from .env file
      load_dotenv(self.config_path)
      self.api_endpoint = os.environ.get('API_ENDPOINT')
      self.api_key = os.environ.get('API_KEY')
      self.default_model = os.environ.get('DEFAULT_MODEL')
      
      print(f"{Colors.GREEN}{Colors.BOLD}Basic Configuration:{Colors.RESET}")
      print(f"{Colors.BLUE}{Colors.BOLD}API_ENDPOINT: {self.api_endpoint}{Colors.RESET}")
      print(f"{Colors.BLUE}{Colors.BOLD}DEFAULT_MODEL: {self.default_model}{Colors.RESET}")