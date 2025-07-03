import unittest
import re
from ..src.llm_tools.prompt_refiner import PromptRefiner

class TestPromptRefiner(unittest.TestCase):
    def setUp(self):
        self.refiner = PromptRefiner(verbose=False)
        self.verbose_refiner = PromptRefiner(verbose=True)

    def test_combine_refinement_prompt(self):
        input_prompt = "This is my original prompt."
        refinement_prompt = "Please refine the following prompt:"
        expected_output = "Please refine the following prompt:\n <original_prompt>\nThis is my original prompt.\n</original_prompt>"
        self.assertEqual(self.refiner.combine_refinement_prompt(input_prompt, refinement_prompt), expected_output)

        with self.assertRaises(ValueError):
            self.refiner.combine_refinement_prompt("", refinement_prompt)

    def test_format_as_markdown(self):
        # Test case where content is already markdown
        markdown_content = "# Hello\n**World**"
        self.assertEqual(self.refiner.format_as_markdown(markdown_content), markdown_content)

        # Test case where content is plain text
        plain_text_content = "This is plain text."
        # markdownify converts plain text to markdown, typically by escaping special characters
        # and sometimes adding paragraph tags. We'll check if it's been processed.
        # The exact output of markdownify can vary slightly, so we'll check for a reasonable transformation.
        formatted_content = self.refiner.format_as_markdown(plain_text_content)
        self.assertIsInstance(formatted_content, str)
        self.assertNotEqual(formatted_content, plain_text_content) # Should be transformed

    def test_clean_response(self):
        # Test removal of think blocks and similar meta-commentary
        response_with_meta = "<think>This is a thought.</think>Actual content.<analysis>Some analysis.</analysis>"
        self.assertEqual(self.refiner.clean_response(response_with_meta), "Actual content.")

        # Test removal of common prefixes
        response_with_prefix = "Here's the refined prompt: My refined content."
        self.assertEqual(self.refiner.clean_response(response_with_prefix), "My refined content.")

        # Test removal of excessive whitespace
        response_with_whitespace = "Line 1.\n\n\nLine 2.\n\n"
        self.assertEqual(self.refiner.clean_response(response_with_whitespace), "Line 1.\n\nLine 2.")

        # Test removal of stray tags
        response_with_stray_tags = "Content with </think>stray<tool_code> tags."
        self.assertEqual(self.refiner.clean_response(response_with_stray_tags), "Content with stray tags.")
        
        # Test with multiple types of cleaning
        complex_response = """
        <thinking>Initial thoughts</thinking>
        Here's the refined prompt:

        This is the actual refined content.

        <meta>Some meta info</meta>
        And more content.
        </response>
        """
        expected_complex_cleaned = "This is the actual refined content.\n\nAnd more content."
        self.assertEqual(self.refiner.clean_response(complex_response), expected_complex_cleaned)

        # Test with no cleaning needed
        clean_response_text = "This is a clean response."
        self.assertEqual(self.refiner.clean_response(clean_response_text), clean_response_text)

    def test_clean_response_from_markdown(self):
        # Test removal of markdown code block formatting
        markdown_code_block = "```python\nprint('Hello')\n```"
        self.assertEqual(self.refiner.clean_response_from_markdown(markdown_code_block), "print('Hello')")

        # Test with multiple code blocks and other content
        mixed_markdown = """
        Some text before.
        ```javascript
        console.log('JS');
        ```
        Some text in between.
        ```
        Plain code block.
        ```
        Text after.
        """
        expected_mixed_cleaned = """
        Some text before.
        console.log('JS');
        Some text in between.
        Plain code block.
        Text after.
        """
        # Using strip() to handle leading/trailing newlines from the multiline string
        self.assertEqual(self.refiner.clean_response_from_markdown(mixed_markdown).strip(), expected_mixed_cleaned.strip())

        # Test with no markdown code blocks
        no_code_blocks = "Just plain text and some *markdown*."
        self.assertEqual(self.refiner.clean_response_from_markdown(no_code_blocks), no_code_blocks)

if __name__ == '__main__':
    unittest.main()