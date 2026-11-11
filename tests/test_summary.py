import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from notes_app.models import Note
from notes_app.store import load_notes, save_notes
from notes_app.summary import filter_by_tag, summarize, top_tags


def note(text, day, tags=()):
    return Note(text=text, created_at=datetime(2026, 11, day, 9, 0), tags=list(tags))


class SummaryTest(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(summarize([]), "Aucune note.")

    def test_top_tags(self):
        notes = [note("a", 1, ["x"]), note("b", 2, ["x", "y"]), note("c", 3, ["y", "x"])]
        self.assertEqual(top_tags(notes, 1), [("x", 3)])

    def test_summary_lists_most_recent_first(self):
        notes = [note("ancienne", 1), note("récente", 5)]
        out = summarize(notes)
        self.assertIn("2 note(s).", out)
        self.assertLess(out.index("récente"), out.index("ancienne"))

    def test_filter_by_tag(self):
        notes = [note("a", 1, ["x"]), note("b", 2)]
        self.assertEqual([n.text for n in filter_by_tag(notes, "x")], ["a"])


class StoreTest(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "notes.json"
            self.assertEqual(load_notes(path), [])
            save_notes(path, [note("é", 1, ["t"])])
            self.assertEqual(load_notes(path)[0].text, "é")


if __name__ == "__main__":
    unittest.main()
