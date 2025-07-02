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

    # TODO: implement me further
    def postprocess_prompt(self, content, processing_options = {}):
        if self.verbose:
            print("-"*50)
            print("⚙️ PROCESSING OPTIONS", Colors.BRIGHT_YELLOW, "─")
            print("-"*50)
            for key, value in processing_options.items():
                print(key, value, Colors.BRIGHT_YELLOW, Colors.WHITE)
            print()
            print("-"*50)
        
        # Define a regex pattern to match specific internal blocks and their content.
        # This targets blocks like <think>, <tool_code>, <execute_result>, etc.
        # The \1 backreference ensures the closing tag matches the opening tag.
        # re.DOTALL allows '.' to match newlines.
        # The '?' makes '.*?' non-greedy, matching the smallest possible string.
        internal_block_pattern = r'<(think|tool_code|execute_result|response)>.*?</\1>'
        
        # Remove all such internal blocks (including content and tags)
        new_content = re.sub(internal_block_pattern, '', content, flags=re.DOTALL)
        
        # Additionally, remove any stray opening or closing tags for these specific types
        # that might exist without a matching pair (e.g., malformed LLM output).
        stray_tag_pattern = r'</?(think|tool_code|execute_result|response)>'
        new_content = re.sub(stray_tag_pattern, '', new_content, flags=re.DOTALL)

        # Clean up extra newlines and whitespace to ensure only the refined prompt remains.
        # Split into lines, strip leading/trailing whitespace from each line.
        lines = [line.strip() for line in new_content.splitlines()]
        
        # Join lines, collapsing multiple empty lines into at most one empty line for paragraph breaks.
        cleaned_content = []
        prev_line_empty = False
        for line in lines:
            if line: # If line is not empty
                cleaned_content.append(line)
                prev_line_empty = False
            elif not prev_line_empty and cleaned_content: # If line is empty and previous was not, and not the very first line
                cleaned_content.append('') # Add one empty line for paragraph break
                prev_line_empty = True
        
        # Final strip for overall leading/trailing whitespace and join with newlines.
        new_content = '\n'.join(cleaned_content).strip()

        if self.verbose:
            print("-"*50)
            print("🎯 GENERATED PROMPT (POST-PROCESSED)", Colors.BRIGHT_MAGENTA, "═")
            print(f"{Colors.DIM}{new_content}{Colors.RESET}\n")
            print("-"*50)
        return new_content
      
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