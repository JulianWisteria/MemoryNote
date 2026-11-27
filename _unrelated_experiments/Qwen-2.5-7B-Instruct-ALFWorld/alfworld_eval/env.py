from __future__ import annotations

import logging
from typing import Any

from .config import Config
from .parsing import (
    ActionParseError,
    is_nothing_happened,
    parse_action,
    to_move_syntax,
)
from .state import EpisodeState

logger = logging.getLogger("alfworld_eval")

PARSE_ERROR_OBS = "Observation: Error Input. Your input must contains 'Action: '"
NOTE_OBS_SUFFIX = "\n\nThis note may help you complete the task:\n{note}"


def _first(x: Any) -> Any:
    if isinstance(x, str):
        return x
    if isinstance(x, (list, tuple)):
        return x[0] if x else None
    try:  # numpy arrays
        return x[0]
    except Exception:
        return x


def process_ob(ob: str) -> str:
    """Drop TextWorld's repetitive arrival prefix."""
    if ob.startswith("You arrive at loc "):
        idx = ob.find(". ")
        if idx != -1:
            return ob[idx + 2 :]
    return ob


class InteractiveEnv:
    """One ALFWorld episode: prompt in, Thought/Action out, env.step, repeat."""

    def __init__(
        self,
        task: Any,
        prompt: str,
        cfg: Config,
        note: str | None = None,
    ):
        self.task = task
        self.env = task.env
        self.cfg = cfg
        self.prompt = prompt
        self.note = note
        self.admissible = list(getattr(task, "admissible_commands", []) or [])
        self.state = EpisodeState(note=note)

    def reset(self) -> tuple[str, EpisodeState]:
        self.state = EpisodeState(note=self.note)
        self.state.history.append({"role": "user", "content": self.prompt})
        return self.prompt, self.state

    def step(self, llm_output: str) -> tuple[str, EpisodeState]:
        self.state.history.append({"role": "assistant", "content": llm_output})

        try:
            action = parse_action(llm_output, self.cfg.prompt.parser)
        except ActionParseError as e:
            logger.debug("parse error: %s | raw=%r", e, llm_output[:400])
            return self._parse_error()

        action = self._adapt_action(action)
        self.state.actions.append(action)
        try:
            observation, reward, done, info = self.env.step([action])
        except Exception as e:
            logger.warning("env.step failed for action %r: %s", action, e)
            return self._parse_error()

        if isinstance(info, dict) and info.get("admissible_commands"):
            self.admissible = list(info["admissible_commands"][0])

        obs = process_ob(str(_first(observation)))
        done = bool(_first(done))

        won = info.get("won") if isinstance(info, dict) else None
        if won is not None:
            reward_value = float(_first(won))
        else:
            reward_value = float(_first(reward) or 0.0)

        obs_full = f"Observation: {obs}"
        if is_nothing_happened(obs):
            self.state.invalid_actions += 1
        if self.note and self.cfg.run.note_mode == "observation":
            obs_full += NOTE_OBS_SUFFIX.format(note=self.note)

        self.state.history.append({"role": "user", "content": obs_full})
        self.state.observations.append(obs)
        self.state.steps += 1

        if done:
            self.state.finished = True
            self.state.success = True
            self.state.terminate_reason = "success"
            self.state.reward = reward_value
        elif self.state.steps >= self.cfg.env.max_steps:
            self.state.finished = True
            self.state.success = False
            self.state.terminate_reason = "max_steps"
            self.state.reward = reward_value

        return obs_full, self.state

    def _adapt_action(self, action: str) -> str:
        """Bridge ``put/place`` to the TextWorld ``move`` verb when needed."""
        syntax = self.cfg.env.action_syntax
        if syntax == "put":
            return action
        moved = to_move_syntax(action)
        if syntax == "move":
            return moved or action
        # auto: rewrite only when the environment advertises the move form.
        if moved and self.admissible and action not in self.admissible:
            if moved in self.admissible:
                logger.debug("action rewrite: %r -> %r", action, moved)
                return moved
        return action

    def _parse_error(self) -> tuple[str, EpisodeState]:
        self.state.parse_errors += 1
        self.state.steps += 1
        self.state.history.append({"role": "user", "content": PARSE_ERROR_OBS})

        if self.state.parse_errors >= self.cfg.env.max_bad_steps:
            self.state.finished = True
            self.state.success = False
            self.state.terminate_reason = "max_bad_steps"
            self.state.reward = 0.0
        elif self.state.steps >= self.cfg.env.max_steps:
            self.state.finished = True
            self.state.success = False
            self.state.terminate_reason = "max_steps"
            self.state.reward = 0.0

        return PARSE_ERROR_OBS, self.state
