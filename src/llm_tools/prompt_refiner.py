from .colors import Colors
import re
from markdownify import markdownify as md

"""
A class for refining prompts using LLM API calls.
"""
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
        return f"{refinement_prompt}\n\n{input_prompt}"
      
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

    def clean_response(self, response: str) -> str:
        """Clean the refined response by removing meta-elements"""
        if self.verbose:
            print(f"{Colors.MAGENTA}Cleaning refined response...{Colors.RESET}")
        
        original_length = len(response)
        cleaned = response
        
        # Remove think blocks and similar meta-commentary
        patterns_to_remove = [
            r'<think>.*?</think>',  # Think blocks
            r'<thinking>.*?</thinking>',  # Thinking blocks
            r'<analysis>.*?</analysis>',  # Analysis blocks
            r'<reasoning>.*?</reasoning>',  # Reasoning blocks
            r'<meta>.*?</meta>',  # Meta blocks
            r'<reflection>.*?</reflection>',  # Reflection blocks
        ]
        
        for pattern in patterns_to_remove:
            matches = re.findall(pattern, cleaned, re.DOTALL | re.IGNORECASE)
            if matches:
                if self.verbose:
                    print(f"{Colors.BLUE}Removing {len(matches)} instances of pattern: {pattern}{Colors.RESET}")
                cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove common prefixes that models might add
        prefixes_to_remove = [
            r'^Here\'s the refined prompt:\s*',
            r'^Refined prompt:\s*',
            r'^The refined prompt is:\s*',
            r'^Here is the refined version:\s*',
            r'^Refined version:\s*',
        ]
        
        for prefix in prefixes_to_remove:
            if re.match(prefix, cleaned, re.IGNORECASE):
                cleaned = re.sub(prefix, '', cleaned, flags=re.IGNORECASE)
                if self.verbose:
                    print(f"{Colors.BLUE}Removed prefix pattern: {prefix}{Colors.RESET}")
        
        # Clean up excessive whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)  # Max 2 consecutive newlines
        
        # remove stray tags from the response
        stray_tag_pattern = r'</?(think|tool_code|execute_result|response)>'
        cleaned = re.sub(stray_tag_pattern, '', cleaned, flags=re.DOTALL)
        
        stray_tag_pattern = r'<?(think|tool_code|execute_result|response)>'
        cleaned = re.sub(stray_tag_pattern, '', cleaned, flags=re.DOTALL)
        
        # remove trailing and leading whitespace
        cleaned = cleaned.strip()
        
        chars_removed = original_length - len(cleaned)
        if chars_removed > 0:
            if self.verbose:
                print(f"{Colors.GREEN}Cleaned response: removed {chars_removed} characters{Colors.RESET}")
        else:
            if self.verbose:
                print(f"{Colors.BLUE}No cleaning needed - response was already clean{Colors.RESET}")
        
        if self.verbose:
            print(f"{Colors.BLUE}Final cleaned length: {len(cleaned)} characters{Colors.RESET}")
        return cleaned
    
    def clean_response_from_markdown(self, content):
        original_length = len(content)
        
        # Remove all markdown code block formatting from the content
        pattern = r'```(?:\n|(?:json|yml|yaml|javascript|html)\n)'
        cleaned = re.sub(pattern, '', content, flags=re.DOTALL)
        
        chars_removed = original_length - len(cleaned)
        if chars_removed > 0:
            if self.verbose:
                print(f"{Colors.GREEN}Cleaned response: removed {chars_removed} characters{Colors.RESET}")
        else:
            if self.verbose:
                print(f"{Colors.BLUE}No cleaning needed - response was already clean{Colors.RESET}")
        
        if self.verbose:
            print(f"{Colors.BLUE}Final cleaned length: {len(cleaned)} characters{Colors.RESET}")
            
        return cleaned
