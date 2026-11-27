from __future__ import annotations

import json
import logging
import os
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .config import Config
from .env import InteractiveEnv
from .notes import NoteStore
from .prompting import TASK_TYPES, build_prompt, load_assets, validate_icl
from .tasks import iter_tasks, load_environment

logger = logging.getLogger("alfworld_eval")


def setup_logging(log_path: Path, verbose: bool = False) -> None:
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.propagate = False
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%H:%M:%S")
    stream = logging.StreamHandler()
    stream.setFormatter(fmt)
    logger.addHandler(stream)

    log_path.parent.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)


def _task_record(
    task: Any, state: Any, prompt: str, cfg: Config, split_name: str
) -> dict[str, Any]:
    return {
        "task_id": task.task_id,
        "task_name": task.name,
        "task_type": task.task_type,
        "split": split_name,
        "prompt": prompt,
        "state": state.to_dict(save_history=cfg.run.save_history),
    }


def _load_records(tasks_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(tasks_dir.glob("*.json")):
        try:
            records.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception as e:
            logger.warning("skipping unreadable task file %s: %s", path, e)
    return records


def summarize(
    records: list[dict[str, Any]], cfg: Config, split_name: str
) -> dict[str, Any]:
    n = len(records)
    successes = sum(1 for r in records if r["state"].get("success"))
    rewards = [
        r["state"]["reward"]
        for r in records
        if r["state"].get("reward") is not None
    ]
    steps = [r["state"].get("steps", 0) for r in records]

    by_type: dict[str, dict[str, int]] = defaultdict(
        lambda: {"n": 0, "success": 0, "invalid_actions": 0, "parse_errors": 0}
    )
    for r in records:
        bucket = by_type[r["task_type"]]
        bucket["n"] += 1
        bucket["success"] += int(bool(r["state"].get("success")))
        bucket["invalid_actions"] += int(r["state"].get("invalid_actions", 0))
        bucket["parse_errors"] += int(r["state"].get("parse_errors", 0))

    for bucket in by_type.values():
        bucket["success_rate"] = bucket["success"] / bucket["n"] if bucket["n"] else None

    terminate = Counter(r["state"].get("terminate_reason") for r in records)

    return {
        "model": cfg.model.name,
        "split": cfg.env.split,
        "alfworld_split": split_name,
        "n_tasks": n,
        "success_rate": successes / n if n else None,
        "avg_reward": sum(rewards) / len(rewards) if rewards else None,
        "avg_steps": sum(steps) / n if n else None,
        "terminate_reasons": dict(terminate),
        "by_task_type": {k: dict(v) for k, v in sorted(by_type.items())},
        "config": cfg.snapshot(),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }


def run(cfg: Config, agent: Any, verbose: bool = False) -> dict[str, Any]:
    out_dir = cfg.resolve(cfg.run.output_dir)
    assert out_dir is not None
    tasks_dir = out_dir / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(out_dir / "log.txt", verbose=verbose)

    instruction_path = cfg.resolve(cfg.prompt.instruction_path)
    icl_path = cfg.resolve(cfg.prompt.icl_path)
    assert instruction_path is not None and icl_path is not None
    instruction, icl = load_assets(instruction_path, icl_path)
    icl_errors = validate_icl(icl)
    if icl_errors:
        raise SystemExit("invalid ICL asset:\n  " + "\n  ".join(icl_errors))

    note_store = NoteStore(cfg.resolve(cfg.run.notes_path), mode=cfg.run.note_mode)

    records = _load_records(tasks_dir) if cfg.run.resume else []
    done_ids = {int(r["task_id"]) for r in records if "task_id" in r}
    per_type: Counter[str] = Counter(r["task_type"] for r in records)
    if records:
        logger.info("resume: %d tasks already done in %s", len(records), out_dir)

    env, n_tasks, split_name = load_environment(cfg.env.alfworld_data, cfg.env.split)
    logger.info(
        "split=%s (%s) | n_tasks=%d | shard=%d/%d | max_steps=%d | parser=%s",
        cfg.env.split,
        split_name,
        n_tasks,
        cfg.run.shard_index,
        cfg.run.num_shards,
        cfg.env.max_steps,
        cfg.prompt.parser,
    )

    tasks = iter_tasks(
        env,
        n_tasks,
        keep_room_description=cfg.env.keep_room_description,
        num_shards=cfg.run.num_shards,
        shard_index=cfg.run.shard_index,
    )

    run_count = 0
    t0 = time.time()
    for task in tasks:
        if task.task_id in done_ids:
            continue
        if (
            cfg.run.limit_per_type is not None
            and per_type[task.task_type] >= cfg.run.limit_per_type
        ):
            continue

        note = note_store.get(task.task_id, task.task_type, task.name)
        prompt = build_prompt(
            instruction=instruction,
            raw_examples=icl[task.task_type],
            task=task.observation,
            icl_num=cfg.prompt.icl_num,
            note=note if cfg.run.note_mode == "query" else None,
        )

        logger.info(
            "task %d | %s | %s | prompt_chars=%d",
            task.task_id,
            task.task_type,
            task.name,
            len(prompt),
        )
        episode = InteractiveEnv(task, prompt, cfg, note=note)
        episode.reset()

        while not episode.state.finished:
            try:
                output = agent(episode.state.history)
            except Exception as e:
                logger.error("agent failed on task %d: %s", task.task_id, e)
                episode.state.finished = True
                episode.state.success = False
                episode.state.terminate_reason = "api_error"
                episode.state.reward = 0.0
                break

            observation, episode.state = episode.step(output)
            if verbose:
                logger.debug(
                    "step %d | raw=%r | obs=%r",
                    episode.state.steps,
                    output[:300],
                    observation[:300],
                )

        record = _task_record(task, episode.state, prompt, cfg, split_name)
        path = tasks_dir / f"{task.task_id:04d}.json"
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(
            json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        os.replace(tmp, path)

        records.append(record)
        per_type[task.task_type] += 1
        run_count += 1

        logger.info(
            "task %d done | success=%s steps=%d reward=%s reason=%s parse_errors=%d invalid_actions=%d",
            task.task_id,
            episode.state.success,
            episode.state.steps,
            episode.state.reward,
            episode.state.terminate_reason,
            episode.state.parse_errors,
            episode.state.invalid_actions,
        )

        if cfg.run.limit is not None and run_count >= cfg.run.limit:
            logger.info("reached --limit %d", cfg.run.limit)
            break
        if cfg.run.limit_per_type is not None and all(
            per_type[t] >= cfg.run.limit_per_type for t in TASK_TYPES
        ):
            logger.info(
                "reached --limit-per-type %d for all task types",
                cfg.run.limit_per_type,
            )
            break

    summary = summarize(records, cfg, split_name)
    summary_name = (
        "summary.json"
        if cfg.run.num_shards == 1
        else f"summary_shard{cfg.run.shard_index}.json"
    )
    (out_dir / summary_name).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    logger.info(
        "done in %.1fs | n=%d | success_rate=%s | avg_reward=%s | avg_steps=%s",
        time.time() - t0,
        summary["n_tasks"],
        summary["success_rate"],
        summary["avg_reward"],
        summary["avg_steps"],
    )
    return summary
