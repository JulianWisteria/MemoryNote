import unittest
from pathlib import Path

from alfworld_eval.prompting import (
    TASK_TYPES,
    build_examples,
    build_prompt,
    load_assets,
    validate_icl,
)

ROOT = Path(__file__).resolve().parents[1]

ICL_ONE = [
    [
        {"role": "user", "content": "ENV DESC"},
        {"role": "assistant", "content": "Thought: t1\nAction: go to cabinet 1"},
        {"role": "user", "content": "Observation: You see a mug."},
        {"role": "assistant", "content": "Action: take mug 1 from cabinet 1"},
    ]
]


class TestPrompting(unittest.TestCase):
    def test_template_order(self):
        prompt = build_prompt("INSTR", ICL_ONE, "TASK LINE", icl_num=1)
        self.assertTrue(prompt.startswith("INSTR\n---\nHere is an example."))
        self.assertIn("ENV DESC", prompt)
        self.assertIn("Action: take mug 1 from cabinet 1", prompt)
        self.assertIn(
            "Now, it's your turn and here is the task.\nTASK LINE", prompt
        )

    def test_note_appended(self):
        prompt = build_prompt("I", ICL_ONE, "T", note="hello")
        self.assertTrue(prompt.endswith("Additional note:\nhello"))

    def test_two_shot_labels(self):
        prompt = build_prompt("I", [ICL_ONE[0], ICL_ONE[0]], "T", icl_num=2)
        self.assertIn("Here are 2 examples.", prompt)
        self.assertIn("Example task 2:", prompt)

    def test_zero_shot_has_no_demo(self):
        prompt = build_prompt("INSTR", ICL_ONE, "TASK LINE", icl_num=0)
        self.assertIn("INSTR", prompt)
        self.assertIn("Now, it's your turn and here is the task.\nTASK LINE", prompt)
        self.assertNotIn("Here is an example", prompt)
        self.assertNotIn("ENV DESC", prompt)

    def test_zero_shot_with_note(self):
        prompt = build_prompt("I", ICL_ONE, "T", icl_num=0, note="hello")
        self.assertTrue(prompt.endswith("Additional note:\nhello"))

    def test_build_examples_one_shot(self):
        examples = build_examples(ICL_ONE, icl_num=1)
        self.assertTrue(examples.startswith("ENV DESC\n"))
        self.assertIn("Thought: t1\nAction: go to cabinet 1\n", examples)

    def test_real_assets(self):
        instruction, icl = load_assets(
            ROOT / "prompts/alfworld_inst.txt",
            ROOT / "prompts/alfworld_icl.json",
        )
        self.assertEqual(set(icl), set(TASK_TYPES))
        for task_type in TASK_TYPES:
            self.assertEqual(len(icl[task_type]), 3)
            self.assertTrue(icl[task_type][0])
        self.assertEqual(validate_icl(icl), [])
        self.assertIn("go to {recep}", instruction)
        self.assertIn("Action:", instruction)


if __name__ == "__main__":
    unittest.main()
