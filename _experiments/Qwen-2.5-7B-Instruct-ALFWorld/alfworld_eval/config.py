from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class ModelConfig:
    name: str = "Qwen2.5-7B-Instruct"
    api_base: str = "http://localhost:8000/v1"
    api_key: str = "EMPTY"
    temperature: float = 0.0
    max_tokens: int = 512
    # vLLM accepts both; fall back to max_tokens automatically if needed.
    token_param: str = "max_completion_tokens"
    seed: int | None = 0
    request_timeout: float = 180.0
    max_retries: int = 6
    extra_body: dict[str, Any] = field(default_factory=dict)


@dataclass
class EnvConfig:
    alfworld_data: str | None = None
    split: str = "test"  # train | dev (seen) | test (unseen)
    max_steps: int = 30
    max_bad_steps: int = 50
    # MPO drops the first paragraph of the reset observation and keeps only
    # "Your task is to: ...". Set true to keep the room description too.
    keep_room_description: bool = False
    # ALFWorld 0.4.x advertises `move X to Y`; the MPO prompt uses
    # `put X in/on Y`. auto rewrites only when the environment asks for move.
    action_syntax: str = "auto"  # auto | put | move


@dataclass
class PromptConfig:
    instruction_path: str = "prompts/alfworld_inst.txt"
    icl_path: str = "prompts/alfworld_icl.json"
    icl_num: int = 1
    parser: str = "lenient"  # lenient | strict_mpo


@dataclass
class RunConfig:
    output_dir: str = "runs/qwen2.5-7b"
    num_shards: int = 1
    shard_index: int = 0
    resume: bool = True
    limit: int | None = None
    limit_per_type: int | None = None
    save_history: bool = True
    notes_path: str | None = None
    note_mode: str = "query"  # query | observation | none


@dataclass
class Config:
    model: ModelConfig = field(default_factory=ModelConfig)
    env: EnvConfig = field(default_factory=EnvConfig)
    prompt: PromptConfig = field(default_factory=PromptConfig)
    run: RunConfig = field(default_factory=RunConfig)

    def resolve(self, p: str | None) -> Path | None:
        if p is None:
            return None
        path = Path(os.path.expanduser(str(p)))
        return path if path.is_absolute() else (PROJECT_ROOT / path)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.env.split not in {"train", "dev", "test"}:
            errors.append(f"env.split must be train|dev|test, got {self.env.split!r}")
        if self.prompt.parser not in {"lenient", "strict_mpo"}:
            errors.append(
                f"prompt.parser must be lenient|strict_mpo, got {self.prompt.parser!r}"
            )
        if self.prompt.icl_num < 0:
            errors.append("prompt.icl_num must be >= 0 (0 = zero-shot)")
        if self.env.max_steps < 1:
            errors.append("env.max_steps must be >= 1")
        if self.env.max_bad_steps < 1:
            errors.append("env.max_bad_steps must be >= 1")
        if self.env.action_syntax not in {"auto", "put", "move"}:
            errors.append(
                "env.action_syntax must be auto|put|move, "
                f"got {self.env.action_syntax!r}"
            )
        if self.run.num_shards < 1:
            errors.append("run.num_shards must be >= 1")
        if not (0 <= self.run.shard_index < max(1, self.run.num_shards)):
            errors.append(
                "run.shard_index must satisfy 0 <= shard_index < num_shards"
            )
        if self.run.note_mode not in {"query", "observation", "none"}:
            errors.append(
                "run.note_mode must be query|observation|none, "
                f"got {self.run.note_mode!r}"
            )
        for key in ("instruction_path", "icl_path"):
            p = self.resolve(getattr(self.prompt, key))
            if p is None or not p.exists():
                errors.append(f"prompt.{key} does not exist: {p}")
        if self.run.notes_path:
            p = self.resolve(self.run.notes_path)
            if p is None or not p.exists():
                errors.append(f"run.notes_path does not exist: {p}")
        return errors

    def snapshot(self) -> dict[str, Any]:
        return asdict(self)


def load_config(path: str | Path) -> Config:
    """Load a YAML config. Relative paths are resolved against PROJECT_ROOT."""
    import yaml

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    cfg = Config(
        model=ModelConfig(**raw.get("model", {})),
        env=EnvConfig(**raw.get("env", {})),
        prompt=PromptConfig(**raw.get("prompt", {})),
        run=RunConfig(**raw.get("run", {})),
    )
    return cfg
