import json
import tempfile
import unittest
from pathlib import Path

from alfworld_eval.notes import NoteStore


class TestNoteStore(unittest.TestCase):
    def test_json_mapping(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "notes.json"
            path.write_text(
                json.dumps({"12": "task note", "pick_and_place": "type note"}),
                encoding="utf-8",
            )
            store = NoteStore(path)
            self.assertEqual(store.get(12), "task note")
            self.assertEqual(store.get(999, "pick_and_place"), "type note")
            self.assertIsNone(store.get(999, "look_at_obj"))

    def test_jsonl_records(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "notes.jsonl"
            path.write_text(
                "\n".join(
                    [
                        json.dumps({"task_id": 12, "note": "by id"}),
                        json.dumps({"task_type": "look_at_obj", "note": "by type"}),
                        json.dumps({"task_name": "foo/bar", "note": "by name"}),
                    ]
                ),
                encoding="utf-8",
            )
            store = NoteStore(path)
            self.assertEqual(store.get(12), "by id")
            self.assertEqual(store.get(999, "look_at_obj"), "by type")
            self.assertEqual(store.get(999, "other", "foo/bar"), "by name")

    def test_single_jsonl_record(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "notes.json"
            path.write_text(
                json.dumps({"task_id": 7, "note": "one record"}),
                encoding="utf-8",
            )
            store = NoteStore(path)
            self.assertEqual(store.get(7), "one record")

    def test_mode_none_disables_notes(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "notes.json"
            path.write_text(json.dumps({"12": "task note"}), encoding="utf-8")
            store = NoteStore(path, mode="none")
            self.assertIsNone(store.get(12))


if __name__ == "__main__":
    unittest.main()
