import tempfile
import unittest
from pathlib import Path
from unittest import mock

from alfworld_eval.config import Config
from alfworld_eval.runner import run
from alfworld_eval.tasks import Task


class FakeEnv:
    def __init__(self, done_after: int = 1):
        self.i = 0
        self.done_after = done_after

    def step(self, actions):
        self.i += 1
        done = self.i >= self.done_after
        return (
            ["You arrive at loc 1. You see a mug."],
            [0.0],
            [done],
            {"won": [1.0 if done else 0.0]},
        )


class FakeAgent:
    def __init__(self, output: str = "Action: go to cabinet 1"):
        self.output = output
        self.calls = 0

    def __call__(self, messages):
        self.calls += 1
        return self.output


class TestRunner(unittest.TestCase):
    def test_end_to_end_and_resume(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = Config()
            cfg.run.output_dir = d
            cfg.run.save_history = False

            tasks = [
                Task(0, "pick_and_place/a", "pick_and_place", "do a", FakeEnv(1)),
                Task(1, "look_at_obj/b", "look_at_obj", "do b", FakeEnv(2)),
            ]
            agent = FakeAgent()

            with mock.patch(
                "alfworld_eval.runner.load_environment",
                return_value=(None, 2, "eval_out_of_distribution"),
            ), mock.patch(
                "alfworld_eval.runner.iter_tasks",
                return_value=iter(tasks),
            ):
                summary = run(cfg, agent)

            self.assertEqual(summary["n_tasks"], 2)
            self.assertEqual(summary["success_rate"], 1.0)
            self.assertEqual(summary["avg_reward"], 1.0)
            self.assertTrue((Path(d) / "summary.json").exists())
            self.assertEqual(len(list((Path(d) / "tasks").glob("*.json"))), 2)

            calls_after_first = agent.calls

            # Re-running with resume should skip both completed tasks.
            with mock.patch(
                "alfworld_eval.runner.load_environment",
                return_value=(None, 2, "eval_out_of_distribution"),
            ), mock.patch(
                "alfworld_eval.runner.iter_tasks",
                return_value=iter(tasks),
            ):
                summary2 = run(cfg, agent)

            self.assertEqual(summary2["n_tasks"], 2)
            self.assertEqual(agent.calls, calls_after_first)


if __name__ == "__main__":
    unittest.main()
