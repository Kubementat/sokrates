# Task: Provide test code

Provide test code for the following class. Ensure to test all edge cases and try to cover between 90 and 100% of the code of the class.

<class_to_test>
from .colors import Colors
import re
from markdownify import markdownify as md

class PromptRefiner:
    def __init__(self, config={}, verbose=False):
        self.config = config
        self.verbose = verbose

    def combine_refinement_prompt(self, input_prompt, refinement_prompt):
        """
        Combine an input prompt with a refinement prompt.

        Args:
            input_prompt (str): Initial text prompt
            refinement_prompt (str): Contains instructions about prompt refinement and the call to action to refine a given input prompt

        Returns:
            str: Combined prompt
        """
        if len(input_prompt) == 0:
            raise ValueError("Input prompt cannot be empty")
        if self.verbose:
            print("-"*50)
            print("📝 INPUT PROMPT", Colors.BRIGHT_MAGENTA, "═")
            print(f"{Colors.DIM}{input_prompt}{Colors.RESET}\n")
            print("-"*50)
            print("🔧 REFINEMENT PROMPT", Colors.BRIGHT_YELLOW, "═")
            print(f"{Colors.DIM}{refinement_prompt}{Colors.RESET}\n")
            print("-"*50)
        return f"{refinement_prompt}\n <original_prompt>\n{input_prompt}\n</original_prompt>"
      
    def format_as_markdown(self, content):
        """
        Format the LLM output as markdown (if not already formatted).
        
        Args:
            content (str): Raw content from LLM
            
        Returns:
            str: Markdown formatted content
        """
        # If content already appears to be markdown, return as-is
        if any(marker in content for marker in ['#', '**', '*', '`', '```']):
            return content
        
        # Otherwise, wrap in a basic markdown structure
        
        return md(content)
</class_to_test>


NOW WRITE THE TESTS and provide instructions on how to run the tests against the class. Make sure to include all necessary imports and setup code.