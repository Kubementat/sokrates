# Project Summary: sokrates

## 1. Key Technical Concepts
- **LLM Interaction Framework**: Comprehensive tools for working with Large Language Models (LLMs) through modular components and well-documented APIs.
- **Prompt Refinement**: Advanced techniques for optimizing LLM input/output using refinement workflows.
- **System Monitoring**: Real-time tracking of resource usage during LLM operations (CPU, memory, GPU).
- **CLI Interface**: Extensive command-line tools for rapid experimentation with LLMs.
- **Modular Architecture**: Easily extendable components designed for customization and integration.

## 2. Relevant Files and Code

### Core Components

#### `Config` Class (`src/sokrates/config.py`)
- Manages application-wide configuration settings
- Loads environment variables from `.env` file
- Provides default values for API endpoint, API key, and default model
```python
class Config:
    DEFAULT_API_ENDPOINT = "http://localhost:1234/v1"
    DEFAULT_API_KEY = "notrequired"
    DEFAULT_MODEL = "qwen/qwen3-8b"

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.config_path = f"{str(Path.home())}/.sokrates/.env"
        self.load_env()
```

#### `LLMApi` Class (`src/sokrates/llm_api.py`)
- Handles interactions with OpenAI-compatible LLM APIs
- Provides methods for model listing, text generation, and chat completions
```python
class LLMApi:
    def __init__(self, verbose=False, api_endpoint=Config.DEFAULT_API_ENDPOINT, api_key=Config.DEFAULT_API_KEY):
        self.verbose = verbose
        self.api_endpoint = api_endpoint
        self.api_key = api_key

    def send(self, prompt: str, model: str = Config.DEFAULT_MODEL, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        # Implementation for sending prompts to LLM and receiving responses
```

#### `PromptRefiner` Class (`src/sokrates/prompt_refiner.py`)
- Provides utility functions for processing and cleaning LLM-generated text
- Includes methods for combining prompts and removing unwanted meta-elements
```python
class PromptRefiner:
    def combine_refinement_prompt(self, input_prompt: str, refinement_prompt: str) -> str:
        return f"{refinement_prompt}\n\n{input_prompt}"

    def clean_response(self, response: str) -> str:
        # Implementation for cleaning LLM responses
```

#### `IdeaGenerationWorkflow` Class (`src/sokrates/idea_generation_workflow.py`)
- Orchestrates multi-step workflows for generating and refining prompts using LLMs
```python
class IdeaGenerationWorkflow:
    def __init__(self, api_endpoint: str, api_key: str, idea_count: int = 2,
                 max_tokens: int = 20000, temperature: float = 0.7, verbose: bool = False):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.verbose = verbose
        self.idea_count = idea_count

    def run(self) -> list[str]:
        # Implementation for executing the full idea generation workflow
```

#### `RefinementWorkflow` Class (`src/sokrates/refinement_workflow.py`)
- Orchestrates prompt refinement and execution processes
```python
class RefinementWorkflow:
    def __init__(self, api_endpoint: str = Config.DEFAULT_API_ENDPOINT,
                 api_key: str = Config.DEFAULT_API_KEY,
                 model: str = Config.DEFAULT_MODEL,
                 max_tokens: int = 20000,
                 temperature: float = 0.7,
                 verbose: bool = False):
        self.llm_api = LLMApi(api_endpoint=api_endpoint, api_key=api_key, verbose=verbose)
        self.refiner = PromptRefiner(verbose=verbose)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.verbose = verbose

    def refine_prompt(self, input_prompt: str, refinement_prompt: str, context_array: List[str]=None) -> str:
        # Implementation for refining prompts
```

#### `SequentialTaskExecutor` Class (`src/sokrates/sequential_task_executor.py`)
- Executes tasks defined in JSON files sequentially using LLM workflows
```python
class SequentialTaskExecutor:
    def __init__(self, api_endpoint: str = Config.DEFAULT_API_ENDPOINT,
                 api_key: str = Config.DEFAULT_API_KEY,
                 model: str = Config.DEFAULT_MODEL,
                 output_dir: str = None,
                 verbose: bool = False):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.model = model
        self.output_dir = output_dir or "./task_results"
        self.verbose = verbose

    def execute_tasks_from_file(self, task_file_path: str) -> Dict[str, any]:
        # Implementation for executing tasks from JSON file
```

### Utility Components

#### `FileHelper` Class (`src/sokrates/file_helper.py`)
- Provides static methods for common file system operations
```python
class FileHelper:
    @staticmethod
    def read_file(file_path: str, verbose: bool = False) -> str:
        # Implementation for reading files

    @staticmethod
    def write_to_file(file_path: str, content: str, verbose: bool = False) -> None:
        # Implementation for writing files
```

#### `SystemMonitor` Class (`src/sokrates/system_monitor.py`)
- Monitors system resources (CPU, memory, GPU) in real-time
```python
class SystemMonitor:
    def __init__(self, interval: float = 0.5):
        self.interval = interval
        self.system_stats = []
        self.monitoring = False

    def start(self):
        # Implementation for starting system monitoring

    def stop(self):
        # Implementation for stopping system monitoring
```

#### `Colors` Class (`src/sokrates/colors.py`)
- Provides ANSI escape codes for console text formatting
```python
class Colors:
    BLACK: str = '\033[30m'
    RED: str = '\033[91m'
    GREEN: str = '\033[92m'
    # ... other color definitions
```

#### `Utils` Class (`src/sokrates/utils.py`)
- Provides utility functions for common operations
```python
class Utils:
    @staticmethod
    def current_date() -> str:
        return datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def generate_random_int(min_value, max_value):
        if min_value > max_value:
            raise Exception("minimum must be below maximum")
        return random.randint(min_value, max_value)
```

## 3. Simple Usage Examples

### Config Initialization
```python
from src.sokrates.config import Config
config = Config(verbose=True)
print(f"API Endpoint: {config.api_endpoint}")
print(f"Default Model: {config.default_model}")
```

### LLM API Interaction
```python
from src.sokrates.llm_api import LLMApi

api = LLMApi(api_endpoint="http://localhost:1234/v1", verbose=True)
models = api.list_models()
print("Available models:", models)

response = api.send(
    prompt="Explain quantum computing in simple terms",
    model="qwen/qwen3-8b"
)
print("Response:", response)
```

### Prompt Refinement
```python
from src.sokrates.prompt_refiner import PromptRefiner

refiner = PromptRefiner(verbose=True)
input_prompt = "Create a marketing plan for a new product"
refinement_prompt = "Refine the following prompt to be more specific..."

combined_prompt = refiner.combine_refinement_prompt(input_prompt, refinement_prompt)
print("Combined prompt:", combined_prompt)

cleaned_response = refiner.clean_response(response_content)
print("Cleaned response:", cleaned_response)
```

### Idea Generation Workflow
```python
from src.sokrates.idea_generation_workflow import IdeaGenerationWorkflow

workflow = IdeaGenerationWorkflow(
    api_endpoint="http://localhost:1234/v1",
    api_key="your_api_key",
    idea_count=3,
    verbose=True
)

ideas = workflow.run()
for i, idea in enumerate(ideas):
    print(f"Idea {i+1}:\n{idea}\n")
```

### Sequential Task Execution
```python
from src.sokrates.sequential_task_executor import SequentialTaskExecutor

executor = SequentialTaskExecutor(
    api_endpoint="http://localhost:1234/v1",
    model="qwen/qwen3-8b",
    output_dir="./task_results",
    verbose=True
)

results = executor.execute_tasks_from_file("tasks.json")
print("Execution results:", results)
```

### System Monitoring
```python
from src.sokrates.system_monitor import SystemMonitor

monitor = SystemMonitor(interval=0.5)
monitor.start()

# Do some work...
time.sleep(10)

stats = monitor.stop()
for stat in stats:
    print(f"Timestamp: {stat['timestamp']}, CPU: {stat['cpu_percent']}%, Memory: {stat['memory_used_gb']}GB")
```

This summary provides a comprehensive overview of the sokrates project's technical details, core components, and usage examples to facilitate further development and integration with large language models.