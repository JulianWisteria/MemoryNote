import unittest

from alfworld_eval.parsing import (
    ActionParseError,
    is_nothing_happened,
    normalize_action,
    parse_action,
    to_move_syntax,
)


class TestLenientParsing(unittest.TestCase):
    def test_thought_then_action(self):
        out = "Thought: I need a mug.\nAction: go to cabinet 1"
        self.assertEqual(parse_action(out), "go to cabinet 1")

    def test_action_only(self):
        self.assertEqual(parse_action("Action: go to cabinet 1"), "go to cabinet 1")

    def test_lowercase(self):
        self.assertEqual(parse_action("action: go to cabinet 1"), "go to cabinet 1")

    def test_put_in(self):
        self.assertEqual(
            parse_action("Action: put apple 1 in fridge 1"),
            "put apple 1 in/on fridge 1",
        )

    def test_put_on(self):
        self.assertEqual(
            parse_action("Action: put apple 1 on countertop 1"),
            "put apple 1 in/on countertop 1",
        )

    def test_put_in_on(self):
        self.assertEqual(
            parse_action("Action: put apple 1 in/on fridge 1"),
            "put apple 1 in/on fridge 1",
        )

    def test_move_to(self):
        self.assertEqual(
            parse_action("Action: move apple 1 to fridge 1"),
            "put apple 1 in/on fridge 1",
        )

    def test_trailing_observation(self):
        out = "Action: go to cabinet 1\nObservation: You see a mug."
        self.assertEqual(parse_action(out), "go to cabinet 1")

    def test_trailing_task(self):
        out = "Action: go to cabinet 1\nTask: something else"
        self.assertEqual(parse_action(out), "go to cabinet 1")

    def test_multiple_actions_takes_first_line(self):
        out = "Action: go to cabinet 1\nAction: open cabinet 1"
        self.assertEqual(parse_action(out), "go to cabinet 1")

    def test_backticks(self):
        self.assertEqual(parse_action("Action: `go to cabinet 1`"), "go to cabinet 1")

    def test_no_action(self):
        with self.assertRaises(ActionParseError):
            parse_action("Thought: I am thinking only")

    def test_empty(self):
        with self.assertRaises(ActionParseError):
            parse_action("")

    def test_action_label_only(self):
        with self.assertRaises(ActionParseError):
            parse_action("Action:\n")


class TestStrictParsing(unittest.TestCase):
    def test_strict_captures_trailing_text(self):
        out = "Action: go to cabinet 1\nObservation: You see a mug."
        self.assertEqual(
            parse_action(out, mode="strict_mpo"),
            "go to cabinet 1\nObservation: You see a mug.",
        )

    def test_strict_normalizes_put(self):
        self.assertEqual(
            parse_action("Action: put apple 1 on fridge 1", mode="strict_mpo"),
            "put apple 1 in/on fridge 1",
        )

    def test_unknown_mode(self):
        with self.assertRaises(ValueError):
            parse_action("Action: go to cabinet 1", mode="nope")


class TestHelpers(unittest.TestCase):
    def test_nothing_happened(self):
        self.assertTrue(is_nothing_happened("Nothing happens."))
        self.assertTrue(is_nothing_happened("Nothing happened"))
        self.assertFalse(is_nothing_happened("You see nothing."))

    def test_normalize_keeps_other_actions(self):
        self.assertEqual(normalize_action("take apple 1 from fridge 1"),
                         "take apple 1 from fridge 1")

    def test_to_move_syntax(self):
        self.assertEqual(
            to_move_syntax("put mug 1 in/on table 1"), "move mug 1 to table 1"
        )
        self.assertEqual(
            to_move_syntax("put mug 1 on table 1"), "move mug 1 to table 1"
        )
        self.assertEqual(
            to_move_syntax("place mug 1 on table 1"), "move mug 1 to table 1"
        )
        self.assertEqual(
            to_move_syntax("move mug 1 to table 1"), "move mug 1 to table 1"
        )
        self.assertIsNone(to_move_syntax("go to table 1"))


if __name__ == "__main__":
    unittest.main()
