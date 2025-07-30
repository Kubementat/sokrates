For the following class: inspect all class definitions, according __init__ functions and method signatures. Display a summary of the file compressing it's functionality description so that it can be added to a coding LLMs context to be able to use the classes and methods for coding tasks. 
Make the output as short as possible but keeping the signatures and a one sentence description of the classes or methods to spare context window space.

```
import logging
import sys
import time
import requests

from openai import OpenAI
from .colors import Colors
class LLMApi:
    def __init__(self, verbose=False):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.verbose = verbose
        
    def get_openai_client(self, api_endpoint="http://localhost:1234/v1", api_key='local-server'):
        """
        Create an OpenAI client instance and return it
        """
        if self.verbose:
            print(f"{Colors.BLUE}{Colors.BOLD}Initializing openai client for endpoint {api_endpoint}...{Colors.RESET}")
        
        # Initialize OpenAI client with custom base URL
        return OpenAI(
            base_url=api_endpoint,
            api_key=api_key
        )

    def list_models(self, api_key, api_endpoint):
        """
        List available models from an OpenAI-compatible endpoint.

        Args:
            api_key (str): API key for authentication
            api_endpoint (str): API endpoint URL

        Returns:
            list: List of model IDs available at the endpoint
        """
        try:
            # Initialize OpenAI client with provided credentials
            client = self.get_openai_client(
                api_key=api_key,
                api_endpoint=api_endpoint
            )
            
            # Fetch and return available models
            models = client.models.list()
            ret_array = []
            for model in models.data:
                ret_array.append(model.id)
            ret_array.sort()
            return ret_array
            
        except Exception as e:
            print(f"{Colors.RED}{Colors.BOLD}Error listing models: {str(e)}{Colors.RESET}")
            raise(e)

    def send(self, prompt, api_endpoint="http://localhost:1234/v1", api_key="local-server",
            model="local-model", max_tokens=2000, temperature=0.7):
        """
        Send a prompt to LLM server and return the response.

        Args:
            prompt (str): The prompt to send
            api_endpoint (str): LLM server API endpoint
            api_key (str): API token for authentication (can be empty for local servers)
            model (str): Model name to use (often not critical for local servers)
            max_tokens (int): Maximum tokens in response

        Returns:
            str: The LLM response content

        Raises:
            Exception: If API call fails
        """
        print(f"{Colors.CYAN}{Colors.BOLD}Generating with model {model} ...{Colors.RESET}", file=sys.stderr)

        try:
            # Initialize OpenAI client with custom base URL
            client = self.get_openai_client(
                api_key=api_key,
                api_endpoint=api_endpoint
            )
            if self.verbose:
                print(f"{Colors.BLUE}{'-'*20}{Colors.RESET}")
                print()
                print(f"{Colors.BLUE}{Colors.BOLD}Prompt:{Colors.RESET}")
                print()
                print(prompt)
                print()
                print(f"{Colors.BLUE}{'-'*20}{Colors.RESET}")
                print()

            # Make API call with custom temperature
            stream = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )

            start_time = time.time()
            first_token_time = None
            print(f"{Colors.GREEN}{'-'*30}{Colors.RESET}")
            print()
            print(f"{Colors.GREEN}{Colors.BOLD}Streaming generation ...{Colors.RESET}")
            print()
            print(f"{Colors.GREEN}{'-'*30}{Colors.RESET}")
            response_content = ""
            for chunk in stream:
                # Each chunk may contain a 'choices' list with a 'delta' dict
                content = chunk.choices[0].delta.content
                if content:
                    if first_token_time is None:
                        first_token_time = time.time()
                    print(content, end="", flush=True)
                    response_content += content

            end_time = time.time()
            if self.verbose:
                print(f"{Colors.GREEN}{'-'*30}{Colors.RESET}")

            print()
            print(f"{Colors.CYAN}{Colors.BOLD}Done generating using model {model}{Colors.RESET}")
            if self.verbose:
                print(f"{Colors.CYAN}Received response ({len(response_content)} characters){Colors.RESET}", file=sys.stderr)
                
            if first_token_time is not None:
                duration_to_first = first_token_time - start_time
                duration_last_to_first = end_time - first_token_time
                total_duration = end_time - start_time
                print(f"{Colors.YELLOW}Time to first token: {duration_to_first:.4f}s")
                print(f"{Colors.YELLOW}Time between first and last token: {duration_last_to_first:.4f}s")
                print(f"{Colors.YELLOW}Total duration: {total_duration:.4f}s")
                
            
            return response_content
        except Exception as e:
            raise Exception(f"{Colors.RED}{Colors.BOLD}Error calling LLM API at {api_endpoint}: {e}{Colors.RESET}")
```