from __future__ import annotations

import logging
import time
from typing import Any

from .config import ModelConfig

logger = logging.getLogger("alfworld_eval")

STOP_WORDS = ["\nObservation:", "\nTask:", "\n---"]


class ChatAgent:
    """Minimal OpenAI-compatible client (works with ``vllm serve``)."""

    def __init__(self, cfg: ModelConfig):
        try:
            from openai import OpenAI
        except ImportError as e:  # pragma: no cover - depends on env
            raise SystemExit(
                "openai is not installed. Install it in the *evaluation* env:\n"
                "  pip install openai"
            ) from e

        self.cfg = cfg
        self.token_param = cfg.token_param
        self.client = OpenAI(
            base_url=cfg.api_base,
            api_key=cfg.api_key,
            timeout=cfg.request_timeout,
        )

    def __call__(self, messages: list[dict[str, str]]) -> str:
        last_err: Exception | None = None
        for attempt in range(self.cfg.max_retries):
            try:
                return self._create(messages)
            except Exception as e:  # network / server errors
                last_err = e
                if attempt == self.cfg.max_retries - 1:
                    raise
                delay = min(2**attempt, 30)
                logger.warning(
                    "LLM call failed (%s); retry %d/%d in %ss",
                    e,
                    attempt + 1,
                    self.cfg.max_retries,
                    delay,
                )
                time.sleep(delay)
        assert last_err is not None
        raise last_err

    def _create(self, messages: list[dict[str, str]]) -> str:
        kwargs: dict[str, Any] = {
            "model": self.cfg.name,
            "messages": messages,
            "temperature": self.cfg.temperature,
            "stop": STOP_WORDS,
            self.token_param: self.cfg.max_tokens,
        }
        if self.cfg.seed is not None:
            kwargs["seed"] = self.cfg.seed
        if self.cfg.extra_body:
            kwargs["extra_body"] = self.cfg.extra_body

        try:
            resp = self.client.chat.completions.create(**kwargs)
        except Exception as e:
            # Older vLLM builds only accept max_tokens.
            if (
                self.token_param == "max_completion_tokens"
                and "max_completion_tokens" in str(e).lower()
            ):
                logger.warning(
                    "Server rejected max_completion_tokens; falling back to max_tokens"
                )
                self.token_param = "max_tokens"
                kwargs.pop("max_completion_tokens", None)
                kwargs["max_tokens"] = self.cfg.max_tokens
                resp = self.client.chat.completions.create(**kwargs)
            else:
                raise

        return resp.choices[0].message.content or ""


def healthcheck(cfg: ModelConfig) -> str:
    """One tiny call; useful before launching a long run."""
    agent = ChatAgent(cfg)
    out = agent([{"role": "user", "content": "Reply with exactly: OK"}])
    return out
