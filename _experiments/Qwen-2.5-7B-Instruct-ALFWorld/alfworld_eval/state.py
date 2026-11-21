from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class EpisodeState:
    history: list[dict[str, str]] = field(default_factory=list)
    steps: int = 0
    reward: float | None = None
    success: bool = False
    finished: bool = False
    terminate_reason: str | None = None
    parse_errors: int = 0
    invalid_actions: int = 0
    actions: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    note: str | None = None

    def to_dict(self, save_history: bool = True) -> dict[str, Any]:
        d = {
            "steps": self.steps,
            "reward": self.reward,
            "success": self.success,
            "finished": self.finished,
            "terminate_reason": self.terminate_reason,
            "parse_errors": self.parse_errors,
            "invalid_actions": self.invalid_actions,
            "actions": self.actions,
            "note": self.note,
        }
        if save_history:
            d["history"] = self.history
        else:
            d["observations"] = self.observations
        return d
