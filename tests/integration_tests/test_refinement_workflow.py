import unittest
from sokrates.workflows.refinement_workflow import RefinementWorkflow
from sokrates import FileHelper

import pytest

class TestRefinementWorkflow(unittest.TestCase):
    def setUp(self):
        self.workflow = RefinementWorkflow(api_endpoint=pytest.TESTING_ENDPOINT, 
                    api_key="not-required",
                    model=pytest.TESTING_MODEL,
                    max_tokens=10000,
                    temperature=0.7,
                    verbose=True)

    def test_refine_prompt(self):
        input_prompt = "This is my original prompt."
        refinement_prompt = "Please refine the following prompt and extend it's width and depth:"
        result = self.workflow.refine_prompt(input_prompt, refinement_prompt)
        # Add assertions to verify the refined prompt
        self.assertTrue(len(result) > 0)
        print("-"*60)
        print("\n Refine and send prompt result:")
        print("-"*60)
        print(result)
        print("-"*60)
        
    def test_refine_and_send_prompt(self):
        input_prompt = "Write a minesweeper clone in Python which can be played on the terminal."
        refinement_prompt = FileHelper.read_file("src/sokrates/prompts/refine-coding-v3.md", verbose=True)
        result = self.workflow.refine_and_send_prompt(input_prompt, refinement_prompt)

        # Add assertions to verify the refined prompt
        self.assertTrue(len(result) > 0)
        print("-"*60)
        print("\n Refine and send prompt result:")
        print("-"*60)
        print(result)
        print("-"*60)

if __name__ == '__main__':
    unittest.main()