import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from notes_app.models import Note
from notes_app.store import load_notes, save_notes
from notes_app.summary import filter_by_tag, remove_note, summarize, top_tags, update_note_text


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


class RemoveNoteTest(unittest.TestCase):
    def test_remove_note(self):
        notes = [note("a", 1), note("b", 2), note("c", 3)]
        removed = remove_note(notes, 1)
        self.assertEqual(removed.text, "b")
        self.assertEqual([n.text for n in notes], ["a", "c"])

    def test_remove_note_invalid_index(self):
        notes = [note("a", 1)]
        with self.assertRaises(IndexError):
            remove_note(notes, 1)
        with self.assertRaises(IndexError):
            remove_note(notes, -1)
        self.assertEqual(len(notes), 1)


class UpdateNoteTextTest(unittest.TestCase):
    def test_update_text_keeps_tags_and_date(self):
        notes = [note("a", 1), note("b", 2, ["x"])]
        update_note_text(notes, 1, "nouveau")
        self.assertEqual(notes[1].text, "nouveau")
        self.assertEqual(notes[1].tags, ["x"])
        self.assertEqual(notes[1].created_at, datetime(2026, 11, 2, 9, 0))
        self.assertEqual(notes[0].text, "a")

    def test_derived_name_follows_new_text(self):
        notes = [note("ancien", 1)]
        update_note_text(notes, 0, "nouveau")
        self.assertEqual(notes[0].name, "nouveau")

    def test_explicit_name_kept(self):
        notes = [Note(text="ancien", created_at=datetime(2026, 11, 1), name="Plombier")]
        update_note_text(notes, 0, "nouveau")
        self.assertEqual(notes[0].name, "Plombier")

    def test_update_invalid_index(self):
        notes = [note("a", 1)]
        with self.assertRaises(IndexError):
            update_note_text(notes, 1, "x")
        with self.assertRaises(IndexError):
            update_note_text(notes, -1, "x")
        self.assertEqual(notes[0].text, "a")


class NameTest(unittest.TestCase):
    def test_default_name_from_text(self):
        self.assertEqual(note("Appeler le plombier", 1).name, "Appeler le plombier")

    def test_default_name_is_truncated_first_line(self):
        n = note("x" * 100 + "\nsuite", 1)
        self.assertLessEqual(len(n.name), 40)
        self.assertNotIn("\n", n.name)

    def test_explicit_name_kept(self):
        n = Note(text="t", created_at=datetime(2026, 11, 1), name="Plombier")
        self.assertEqual(n.name, "Plombier")

    def test_old_note_without_name_gets_default(self):
        data = {"text": "Vieille note", "created_at": "2026-11-01T09:00:00", "tags": []}
        self.assertEqual(Note.from_dict(data).name, "Vieille note")

    def test_name_roundtrip(self):
        n = Note(text="t", created_at=datetime(2026, 11, 1), name="Plombier")
        self.assertEqual(Note.from_dict(n.to_dict()).name, "Plombier")


class StoreTest(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "notes.json"
            self.assertEqual(load_notes(path), [])
            save_notes(path, [note("é", 1, ["t"])])
            self.assertEqual(load_notes(path)[0].text, "é")


if __name__ == "__main__":
    unittest.main()
