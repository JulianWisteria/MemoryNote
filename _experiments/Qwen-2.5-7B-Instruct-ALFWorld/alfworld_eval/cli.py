from __future__ import annotations

import argparse
import json
import sys

from .config import Config, load_config
from .prompting import build_prompt, load_assets, validate_icl
from .tasks import SPLITS


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Evaluate Qwen2.5-7B-Instruct 1-shot ReAct on ALFWorld "
        "(MPO/arXiv:2503.02682 baseline protocol)."
    )
    p.add_argument("--config", default="configs/alfworld_qwen2.5_7b.yaml")
    p.add_argument("--split", choices=["train", "dev", "test"])
    p.add_argument("--model")
    p.add_argument("--api-base")
    p.add_argument("--api-key")
    p.add_argument("--temperature", type=float)
    p.add_argument("--max-tokens", type=int)
    p.add_argument("--seed", type=int)
    p.add_argument("--no-seed", action="store_true")
    p.add_argument("--output-dir")
    p.add_argument("--num-shards", type=int)
    p.add_argument("--shard-index", type=int)
    p.add_argument("--limit", type=int)
    p.add_argument("--limit-per-type", type=int)
    p.add_argument("--notes")
    p.add_argument("--note-mode", choices=["query", "observation", "none"])
    p.add_argument("--icl-num", type=int, help="0 = zero-shot, 1 = one demo")
    p.add_argument("--strict-parser", action="store_true")
    p.add_argument("--no-resume", action="store_true")
    p.add_argument("--no-history", action="store_true")
    p.add_argument("--check", action="store_true", help="validate config/assets only")
    p.add_argument("--list-tasks", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="build prompts, no model calls")
    p.add_argument("--dry-run-n", type=int, default=3)
    p.add_argument("--verbose", action="store_true")
    return p


def apply_overrides(cfg: Config, args: argparse.Namespace) -> None:
    if args.split is not None:
        cfg.env.split = args.split
    if args.model is not None:
        cfg.model.name = args.model
    if args.api_base is not None:
        cfg.model.api_base = args.api_base
    if args.api_key is not None:
        cfg.model.api_key = args.api_key
    if args.temperature is not None:
        cfg.model.temperature = args.temperature
    if args.max_tokens is not None:
        cfg.model.max_tokens = args.max_tokens
    if args.seed is not None:
        cfg.model.seed = args.seed
    if args.no_seed:
        cfg.model.seed = None
    if args.output_dir is not None:
        cfg.run.output_dir = args.output_dir
    if args.num_shards is not None:
        cfg.run.num_shards = args.num_shards
    if args.shard_index is not None:
        cfg.run.shard_index = args.shard_index
    if args.limit is not None:
        cfg.run.limit = args.limit
    if args.limit_per_type is not None:
        cfg.run.limit_per_type = args.limit_per_type
    if args.notes is not None:
        cfg.run.notes_path = args.notes
    if args.note_mode is not None:
        cfg.run.note_mode = args.note_mode
    if args.icl_num is not None:
        cfg.prompt.icl_num = args.icl_num
    if args.strict_parser:
        cfg.prompt.parser = "strict_mpo"
    if args.no_resume:
        cfg.run.resume = False
    if args.no_history:
        cfg.run.save_history = False


def _print_errors(errors: list[str]) -> None:
    print("config check FAILED", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cfg = load_config(args.config)
    apply_overrides(cfg, args)

    errors = cfg.validate()
    if args.check:
        if errors:
            _print_errors(errors)
            return 1
        instruction_path = cfg.resolve(cfg.prompt.instruction_path)
        icl_path = cfg.resolve(cfg.prompt.icl_path)
        assert instruction_path is not None and icl_path is not None
        _, icl = load_assets(instruction_path, icl_path)
        errors = validate_icl(icl)
        if errors:
            _print_errors(errors)
            return 1

        split_name, n_tasks = SPLITS[cfg.env.split]
        print("config check OK")
        print(f"  instruction : {instruction_path}")
        print(f"  icl         : {icl_path}")
        print(f"  task types  : {sorted(icl)}")
        print(f"  split       : {cfg.env.split} ({split_name}, {n_tasks} tasks)")
        print(
            "  run         : "
            f"max_steps={cfg.env.max_steps} icl_num={cfg.prompt.icl_num} "
            f"parser={cfg.prompt.parser} note_mode={cfg.run.note_mode}"
        )
        return 0

    if errors:
        _print_errors(errors)
        return 2

    if args.list_tasks or args.dry_run:
        from .tasks import iter_tasks, load_environment

        instruction_path = cfg.resolve(cfg.prompt.instruction_path)
        icl_path = cfg.resolve(cfg.prompt.icl_path)
        assert instruction_path is not None and icl_path is not None
        instruction, icl = load_assets(instruction_path, icl_path)
        icl_errors = validate_icl(icl)
        if icl_errors:
            _print_errors(icl_errors)
            return 2

        env, n_tasks, split_name = load_environment(
            cfg.env.alfworld_data, cfg.env.split
        )
        print(f"split={cfg.env.split} ({split_name}), n_tasks={n_tasks}")

        shown = 0
        for task in iter_tasks(
            env,
            n_tasks,
            keep_room_description=cfg.env.keep_room_description,
            num_shards=cfg.run.num_shards,
            shard_index=cfg.run.shard_index,
        ):
            if args.list_tasks:
                print(f"{task.task_id:4d}  {task.task_type:24s}  {task.name}")
            else:
                prompt = build_prompt(
                    instruction,
                    icl[task.task_type],
                    task.observation,
                    cfg.prompt.icl_num,
                )
                if shown < args.dry_run_n:
                    print(
                        f"[{task.task_id}] {task.task_type} "
                        f"prompt_chars={len(prompt)} obs_chars={len(task.observation)}"
                    )
                    print("  " + prompt[:500].replace("\n", " | ")[:500] + " ...")
                shown += 1
                if shown >= args.dry_run_n:
                    break

        if args.dry_run:
            print(f"dry-run inspected {shown} tasks")
        return 0

    from .agent import ChatAgent
    from .runner import run

    agent = ChatAgent(cfg.model)
    summary = run(cfg, agent, verbose=args.verbose)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
