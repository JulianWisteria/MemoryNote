from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class NoteStore:
    """Look up an injected note by task id, task type, or task name.

    Accepted file formats
    ---------------------
    JSON object::

        {"12": "note for task 12", "pick_and_place": "note for the family"}

    JSONL::

        {"task_id": 12, "note": "..."}
        {"task_type": "pick_and_place", "note": "..."}

    Lookup order is task_id (str and int), task_type, task_name. This is a hook
    for the note-semantics experiments; the baseline run uses ``notes_path=null``.
    """

    def __init__(self, path: str | Path | None = None, mode: str = "query"):
        self.mode = mode
        self.notes: dict[str, str] = {}
        if path is not None:
            self._load(Path(path))

    def _load(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            return
        if text.startswith("{"):
            try:
                data = json.loads(text)
                if isinstance(data, dict):
                    # A single JSONL-style record, not an id->note mapping.
                    if "note" in data and any(
                        k in data for k in ("task_id", "task_type", "task_name")
                    ):
                        self._add_record(data)
                    else:
                        self.notes = {str(k): str(v) for k, v in data.items()}
                    return
            except json.JSONDecodeError:
                pass
        # JSONL
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            obj: dict[str, Any] = json.loads(line)
            self._add_record(obj)

    def _add_record(self, obj: dict[str, Any]) -> None:
        note = obj.get("note", "")
        if "task_id" in obj:
            self.notes[str(obj["task_id"])] = str(note)
        elif "task_type" in obj:
            self.notes[str(obj["task_type"])] = str(note)
        elif "task_name" in obj:
            self.notes[str(obj["task_name"])] = str(note)
        else:
            raise ValueError(
                "note record needs task_id/task_type/task_name: "
                f"{str(obj)[:120]}"
            )

    def get(
        self,
        task_id: int | str,
        task_type: str | None = None,
        task_name: str | None = None,
    ) -> str | None:
        if self.mode == "none":
            return None
        for key in (str(task_id), task_type, task_name):
            if key is not None and str(key) in self.notes:
                return self.notes[str(key)]
        return None
