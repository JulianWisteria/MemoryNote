from __future__ import annotations

import re


class ActionParseError(ValueError):
    """Raised when a model output contains no usable ``Action:`` field."""


# MPO's exact parser. DOTALL means it captures everything after the first
# "Action:", including trailing junk. Kept for byte-for-byte reproduction.
_ACTION_RE_STRICT = re.compile(r"Action:\s?(.*)", re.DOTALL)

# Default parser: case-insensitive, stops at the first line / next field.
_ACTION_RE_LENIENT = re.compile(r"action\s*:\s*(.+)", re.IGNORECASE | re.DOTALL)
_CUT_RE = re.compile(r"\n\s*(?:observation|task)\s*:|\n\s*---", re.IGNORECASE)

_PUT_RE = re.compile(
    r"^put\s+(.+?)\s+(?:in/on|in|on)\s+(.+?)\s*$", re.IGNORECASE
)
_MOVE_RE = re.compile(r"^move\s+(.+?)\s+to\s+(.+?)\s*$", re.IGNORECASE)
_PLACE_RE = re.compile(
    r"^place\s+(.+?)\s+(?:in/on|in|on|to)\s+(.+?)\s*$", re.IGNORECASE
)

_NOTHING_HAPPENED = {"nothing happened", "nothing happens"}


def normalize_action(action: str) -> str:
    """Normalize ALFWorld placement commands to the canonical ``put X in/on Y``.

    Non-placement commands are returned stripped but otherwise untouched, so
    ``strict_mpo`` mode preserves MPO's exact (possibly multi-line) capture.
    """
    stripped = action.strip()
    compact = " ".join(stripped.split())
    m = _PUT_RE.match(compact)
    if m:
        return f"put {m.group(1).strip()} in/on {m.group(2).strip()}"
    m = _MOVE_RE.match(compact)
    if m:
        return f"put {m.group(1).strip()} in/on {m.group(2).strip()}"
    return stripped


def parse_action(text: str, mode: str = "lenient") -> str:
    """Extract an ALFWorld action from a model response.

    Parameters
    ----------
    text:
        Raw model output.
    mode:
        ``"lenient"`` (default) takes the first line after ``Action:`` and
        strips trailing ``Observation:``/``Task:``/``---`` blocks.
        ``"strict_mpo"`` reproduces MPO's ``re.findall(r"Action:\\s?(.*)", ...)``.
    """
    if not text or not text.strip():
        raise ActionParseError("empty model output")

    if mode == "strict_mpo":
        matches = _ACTION_RE_STRICT.findall(text)
        if not matches:
            raise ActionParseError("no 'Action:' found")
        action = matches[0]
    elif mode == "lenient":
        m = _ACTION_RE_LENIENT.search(text)
        if not m:
            raise ActionParseError("no 'Action:' found")
        action = m.group(1).strip()
        action = _CUT_RE.split(action, maxsplit=1)[0].strip()
        lines = action.splitlines()
        action = lines[0].strip() if lines else ""
    else:
        raise ValueError(f"unknown parser mode: {mode!r}")

    action = action.strip().strip("`\"'").strip()
    if not action:
        raise ActionParseError("empty action after parsing")
    return normalize_action(action)


def to_move_syntax(action: str) -> str | None:
    """Convert a placement command to TextWorld's ``move X to Y`` form.

    Older ALFWorld installs accept ``put X in/on Y``; the 0.4.x TextWorld
    grammars only advertise ``move X to Y``. Returns None if the action is not
    a placement command.
    """
    compact = " ".join(action.strip().split())
    m = _PUT_RE.match(compact) or _PLACE_RE.match(compact) or _MOVE_RE.match(compact)
    if not m:
        return None
    return f"move {m.group(1).strip()} to {m.group(2).strip()}"


def is_nothing_happened(observation: str) -> bool:
    """True if the environment rejected the action as inadmissible."""
    return observation.strip().lower().rstrip(".") in _NOTHING_HAPPENED
