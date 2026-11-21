from __future__ import annotations

import json
from pathlib import Path
from typing import Any

TASK_TYPES = (
    "pick_and_place",
    "pick_clean_then_place",
    "pick_heat_then_place",
    "pick_cool_then_place",
    "look_at_obj",
    "pick_two_obj",
)

# Exact MPO template (prompt/templates.py).
PROMPT_TEMPLATE = """{instruction}
---
{icl_prompt}

{examples}
---

Now, it's your turn and here is the task.
{task}"""

# icl_num=0: no demonstration, only the instruction and the task.
PROMPT_TEMPLATE_ZERO_SHOT = """{instruction}
---

Now, it's your turn and here is the task.
{task}"""

# Note injection hook for the memory experiments. Kept off by default.
NOTE_TEMPLATE = "\n\nAdditional note:\n{note}"


def load_assets(
    instruction_path: str | Path, icl_path: str | Path
) -> tuple[str, dict[str, list[list[dict[str, str]]]]]:
    instruction = Path(instruction_path).read_text(encoding="utf-8")
    icl = json.loads(Path(icl_path).read_text(encoding="utf-8"))
    return instruction, icl


def validate_icl(icl: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = [t for t in TASK_TYPES if t not in icl]
    if missing:
        errors.append(f"ICL is missing task types: {missing}")
    for t in TASK_TYPES:
        if t not in icl:
            continue
        if not isinstance(icl[t], list) or not icl[t]:
            errors.append(f"ICL[{t!r}] is not a non-empty list")
            continue
        for i, example in enumerate(icl[t]):
            if not isinstance(example, list) or not example:
                errors.append(f"ICL[{t!r}][{i}] is not a non-empty message list")
                continue
            for j, msg in enumerate(example):
                if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                    errors.append(f"ICL[{t!r}][{i}][{j}] lacks role/content")
    return errors


def build_examples(
    raw_examples: list[list[dict[str, str]]], icl_num: int = 1
) -> str:
    """Build MPO's ``examples`` string from the selected ICL trajectories."""
    examples = ""
    for i in range(min(icl_num, len(raw_examples))):
        example = raw_examples[i]
        for j, msg in enumerate(example):
            content = msg["content"]
            if i == 0 and j == 0:
                examples += content + "\n"
            elif i != 0 and j == 0:
                if icl_num > 1:
                    examples += f"\nExample task {i + 1}:\n" + content + "\n"
                else:
                    examples += "\n" + content + "\n"
            elif j % 2 == 0:
                examples += content + "\n\n"
            else:
                examples += content + "\n"
    return examples


def build_prompt(
    instruction: str,
    raw_examples: list[list[dict[str, str]]],
    task: str,
    icl_num: int = 1,
    note: str | None = None,
) -> str:
    """Assemble the single user message used by the MPO baseline."""
    if icl_num == 0:
        prompt = PROMPT_TEMPLATE_ZERO_SHOT.format(
            instruction=instruction, task=task
        )
    else:
        examples = build_examples(raw_examples, icl_num)
        icl_prompt = (
            f"Here are {icl_num} examples."
            if icl_num > 1
            else "Here is an example."
        )
        prompt = PROMPT_TEMPLATE.format(
            instruction=instruction,
            icl_prompt=icl_prompt,
            examples=examples,
            task=task,
        )
    if note:
        prompt += NOTE_TEMPLATE.format(note=note)
    return prompt
