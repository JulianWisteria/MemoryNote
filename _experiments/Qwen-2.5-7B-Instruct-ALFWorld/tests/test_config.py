import unittest
from pathlib import Path

from alfworld_eval.config import load_config
from alfworld_eval.tasks import shard_bounds

ROOT = Path(__file__).resolve().parents[1]


class TestConfig(unittest.TestCase):
    def test_load_and_validate(self):
        cfg = load_config(ROOT / "configs/alfworld_qwen2.5_7b.yaml")
        self.assertEqual(cfg.env.split, "test")
        self.assertEqual(cfg.env.max_steps, 30)
        self.assertEqual(cfg.env.action_syntax, "auto")
        self.assertEqual(cfg.prompt.icl_num, 1)
        self.assertEqual(cfg.validate(), [])

    def test_zero_shot_is_valid(self):
        cfg = load_config(ROOT / "configs/alfworld_qwen2.5_7b.yaml")
        cfg.prompt.icl_num = 0
        self.assertEqual(cfg.validate(), [])

    def test_shard_bounds_cover_everything(self):
        for n in (0, 1, 5, 134, 140, 3553):
            for k in range(1, 8):
                bounds = [shard_bounds(n, k, i) for i in range(k)]
                self.assertEqual(bounds[0][0], 0)
                self.assertEqual(bounds[-1][1], n)
                for left, right in zip(bounds, bounds[1:]):
                    self.assertEqual(left[1], right[0])
                self.assertEqual(sum(end - start for start, end in bounds), n)

    def test_shard_bounds_rejects_bad_index(self):
        with self.assertRaises(ValueError):
            shard_bounds(10, 4, 4)


if __name__ == "__main__":
    unittest.main()
