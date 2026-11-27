from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

PREFIXES = {
    "pick_and_place": "put",
    "pick_clean_then_place": "clean",
    "pick_heat_then_place": "heat",
    "pick_cool_then_place": "cool",
    "look_at_obj": "examine",
    "pick_two_obj": "puttwo",
}

# split -> (alfworld split, number of tasks)
SPLITS = {
    "train": ("train", 3553),
    "dev": ("eval_in_distribution", 140),   # seen
    "test": ("eval_out_of_distribution", 134),  # unseen
}


@dataclass
class Task:
    task_id: int
    name: str
    task_type: str
    observation: str
    env: Any
    admissible_commands: list[str] = field(default_factory=list)


def shard_bounds(n: int, num_shards: int, shard_index: int) -> tuple[int, int]:
    if num_shards < 1:
        raise ValueError("num_shards must be >= 1")
    if not 0 <= shard_index < num_shards:
        raise ValueError("shard_index must satisfy 0 <= shard_index < num_shards")
    base, rem = divmod(n, num_shards)
    start = shard_index * base + min(shard_index, rem)
    size = base + (1 if shard_index < rem else 0)
    return start, start + size


def _resolve_data(alfworld_data: str | None) -> Path:
    raw = (
        alfworld_data
        or os.environ.get("ALFWORLD_DATA")
        or os.path.expanduser("~/.cache/alfworld")
    )
    return Path(os.path.expanduser(raw))


def load_environment(
    alfworld_data: str | None, split: str
) -> tuple[Any, int, str]:
    """Create the ALFWorld TextWorld environment for a split."""
    try:
        import yaml
        import alfworld
        import alfworld.agents.environment as envs
        from alfworld.agents.environment.alfred_tw_env import AlfredTWEnv
    except ImportError as e:  # pragma: no cover - depends on env
        raise SystemExit(
            "alfworld is not installed. Use a Python 3.9/3.10 env:\n"
            "  pip install alfworld\n"
            "Then run: alfworld-download"
        ) from e

    if split not in SPLITS:
        raise ValueError(f"unknown split {split!r}; choose from {sorted(SPLITS)}")

    data = _resolve_data(alfworld_data)
    os.environ["ALFWORLD_DATA"] = str(data)

    config_path = data / "base_config.yaml"
    if not config_path.exists():
        raise SystemExit(
            f"ALFWorld data not found at {data}. Run `alfworld-download` or set "
            "ALFWORLD_DATA / env.alfworld_data."
        )
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    split_name, n_tasks = SPLITS[split]
    env_type = config["env"]["type"]

    # alfworld >= 0.4 only exports `get_environment` from
    # `alfworld.agents.environment`; the concrete classes live in submodules.
    env_cls = getattr(envs, env_type, None)
    if env_cls is None:
        import importlib

        for mod_name in ("alfred_tw_env", "alfred_thor_env", "alfred_hybrid"):
            mod = importlib.import_module(
                f"alfworld.agents.environment.{mod_name}"
            )
            if hasattr(mod, env_type):
                env_cls = getattr(mod, env_type)
                break
    if env_cls is None:
        raise SystemExit(f"cannot find ALFWorld environment class {env_type!r}")

    env = env_cls(config, train_eval=split_name)
    assert isinstance(env, AlfredTWEnv)
    env = env.init_env(batch_size=1)
    return env, n_tasks, split_name


def _clean_observation(obs: Any, keep_room: bool) -> str:
    text = str(_first(obs))
    if keep_room:
        return text
    # MPO keeps only the task paragraph: "\n".join(obs.split("\n\n")[1:])
    parts = text.split("\n\n")
    return "\n".join(parts[1:]) if len(parts) > 1 else text


def _first(x: Any) -> Any:
    if isinstance(x, str):
        return x
    if isinstance(x, (list, tuple)):
        return x[0] if x else None
    try:
        return x[0]
    except Exception:
        return x


def iter_tasks(
    env: Any,
    n_tasks: int,
    keep_room_description: bool = False,
    num_shards: int = 1,
    shard_index: int = 0,
) -> Iterator[Task]:
    """Yield tasks for this shard, resetting the shared ALFWorld env."""
    start, end = shard_bounds(n_tasks, num_shards, shard_index)
    if start:
        if hasattr(env, "skip"):
            env.skip(start)
        else:  # pragma: no cover - older alfworld
            for _ in range(start):
                env.reset()

    for local_idx in range(end - start):
        obs, info = env.reset()
        observation = _clean_observation(obs, keep_room_description)
        admissible = []
        if isinstance(info, dict) and info.get("admissible_commands"):
            admissible = list(info["admissible_commands"][0])
        game_file = info["extra.gamefile"][0]
        name = "/".join(game_file.split("/")[-3:-1])

        task_type = None
        for key in PREFIXES:
            if name.startswith(key):
                task_type = key
                break
        if task_type is None:
            raise RuntimeError(f"cannot infer task type from game file: {name}")

        yield Task(
            task_id=start + local_idx,
            name=name,
            task_type=task_type,
            observation=observation,
            env=env,
            admissible_commands=admissible,
        )
