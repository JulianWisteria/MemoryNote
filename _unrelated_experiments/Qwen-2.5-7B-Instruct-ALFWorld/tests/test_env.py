import unittest

from alfworld_eval.config import Config
from alfworld_eval.env import InteractiveEnv, process_ob
from alfworld_eval.tasks import Task


class FakeEnv:
    def __init__(self, dones, wins, observations=None):
        self.dones = dones
        self.wins = wins
        self.observations = observations or [
            "You arrive at loc 1. You see a mug."
        ] * len(dones)
        self.i = 0
        self.seen = []

    def step(self, actions):
        self.seen.append(actions[0])
        j = self.i
        self.i += 1
        return (
            [self.observations[j]],
            [0.0],
            [self.dones[j]],
            {"won": [self.wins[j]]},
        )


def make_task(env):
    return Task(
        task_id=0,
        name="pick_and_place/x",
        task_type="pick_and_place",
        observation="Your task is to: put a mug on the table.",
        env=env,
    )


class TestInteractiveEnv(unittest.TestCase):
    def test_parse_error_is_counted(self):
        cfg = Config()
        cfg.env.max_steps = 5
        episode = InteractiveEnv(make_task(FakeEnv([False], [0.0])), "PROMPT", cfg)
        episode.reset()
        obs, state = episode.step("Thought: no action here")
        self.assertEqual(state.parse_errors, 1)
        self.assertEqual(state.steps, 1)
        self.assertIn("Error Input", obs)
        self.assertFalse(state.finished)

    def test_success(self):
        cfg = Config()
        episode = InteractiveEnv(make_task(FakeEnv([True], [1.0])), "PROMPT", cfg)
        episode.reset()
        _, state = episode.step("Action: go to cabinet 1")
        self.assertTrue(state.success)
        self.assertTrue(state.finished)
        self.assertEqual(state.reward, 1.0)
        self.assertEqual(state.terminate_reason, "success")

    def test_max_steps(self):
        cfg = Config()
        cfg.env.max_steps = 1
        episode = InteractiveEnv(make_task(FakeEnv([False], [0.0])), "PROMPT", cfg)
        episode.reset()
        _, state = episode.step("Action: go to cabinet 1")
        self.assertTrue(state.finished)
        self.assertFalse(state.success)
        self.assertEqual(state.terminate_reason, "max_steps")

    def test_nothing_happened_counts_as_invalid(self):
        cfg = Config()
        cfg.env.max_steps = 5
        env = FakeEnv([False], [0.0], observations=["Nothing happens."])
        episode = InteractiveEnv(make_task(env), "PROMPT", cfg)
        episode.reset()
        _, state = episode.step("Action: go to nowhere 1")
        self.assertEqual(state.invalid_actions, 1)
        self.assertEqual(state.parse_errors, 0)

    def test_process_ob(self):
        self.assertEqual(
            process_ob("You arrive at loc 1. You see a mug."), "You see a mug."
        )
        self.assertEqual(process_ob("Nothing happens."), "Nothing happens.")

    def test_auto_rewrites_put_to_move(self):
        cfg = Config()
        cfg.env.max_steps = 5
        cfg.env.action_syntax = "auto"
        env = FakeEnv([True], [1.0])
        task = make_task(env)
        task.admissible_commands = ["move mug 1 to table 1"]
        episode = InteractiveEnv(task, "PROMPT", cfg)
        episode.reset()
        episode.step("Action: put mug 1 in/on table 1")
        self.assertEqual(env.seen[-1], "move mug 1 to table 1")

    def test_put_syntax_mode_does_not_rewrite(self):
        cfg = Config()
        cfg.env.max_steps = 5
        cfg.env.action_syntax = "put"
        env = FakeEnv([True], [1.0])
        task = make_task(env)
        task.admissible_commands = ["move mug 1 to table 1"]
        episode = InteractiveEnv(task, "PROMPT", cfg)
        episode.reset()
        episode.step("Action: put mug 1 in/on table 1")
        self.assertEqual(env.seen[-1], "put mug 1 in/on table 1")


if __name__ == "__main__":
    unittest.main()
