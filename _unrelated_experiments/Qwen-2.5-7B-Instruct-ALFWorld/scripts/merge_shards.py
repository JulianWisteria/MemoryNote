#!/usr/bin/env python3
"""Merge per-shard task JSONs into one summary (dedupe by task_id)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running as `python scripts/merge_shards.py` from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alfworld_eval.config import load_config  # noqa: E402
from alfworld_eval.runner import _load_records, summarize  # noqa: E402
from alfworld_eval.tasks import SPLITS  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/alfworld_qwen2.5_7b.yaml")
    ap.add_argument("--dirs", nargs="+", required=True)
    ap.add_argument("--out", default="runs/merged_summary.json")
    args = ap.parse_args()

    cfg = load_config(args.config)
    records = []
    for d in args.dirs:
        records.extend(_load_records(Path(d) / "tasks"))

    by_id = {r["task_id"]: r for r in records}
    split_name = SPLITS[cfg.env.split][0]
    merged = summarize(list(by_id.values()), cfg, split_name=split_name)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "n_tasks": merged["n_tasks"],
                "success_rate": merged["success_rate"],
                "avg_reward": merged["avg_reward"],
                "avg_steps": merged["avg_steps"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
