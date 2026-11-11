import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from notes_app.models import Note
from notes_app.store import load_notes, save_notes
from notes_app.summary import (
    filter_by_day,
    filter_by_tag,
    remove_note,
    search_notes,
    summarize,
    top_tags,
)


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


class SearchNotesTest(unittest.TestCase):
    def test_search_in_text_ignores_case(self):
        notes = [note("Appeler le Plombier", 1), note("autre", 2)]
        self.assertEqual([n.text for n in search_notes(notes, "plombier")], ["Appeler le Plombier"])

    def test_search_in_name(self):
        notes = [
            Note(text="x", created_at=datetime(2026, 11, 1), name="Plombier"),
            note("y", 2),
        ]
        self.assertEqual([n.text for n in search_notes(notes, "PLOMB")], ["x"])

    def test_search_in_tags(self):
        notes = [note("a", 1, ["Maison"]), note("b", 2, ["travail"])]
        self.assertEqual([n.text for n in search_notes(notes, "maison")], ["a"])

    def test_search_is_substring(self):
        notes = [note("un chaton", 1)]
        self.assertEqual(len(search_notes(notes, "chat")), 1)

    def test_search_no_match(self):
        self.assertEqual(search_notes([note("a", 1)], "zzz"), [])


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


class FilterByDayTest(unittest.TestCase):
    def test_keeps_only_notes_of_given_day(self):
        notes = [
            Note(text="matin", created_at=datetime(2026, 11, 5, 0, 0)),
            Note(text="soir", created_at=datetime(2026, 11, 5, 23, 59)),
            Note(text="veille", created_at=datetime(2026, 11, 4, 23, 59)),
            Note(text="lendemain", created_at=datetime(2026, 11, 6, 0, 0)),
        ]
        kept = filter_by_day(notes, date(2026, 11, 5))
        self.assertEqual([n.text for n in kept], ["matin", "soir"])

    def test_no_match_gives_empty_list(self):
        notes = [Note(text="a", created_at=datetime(2026, 11, 1))]
        self.assertEqual(filter_by_day(notes, date(2026, 11, 5)), [])


class StoreTest(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "notes.json"
            self.assertEqual(load_notes(path), [])
            save_notes(path, [note("é", 1, ["t"])])
            self.assertEqual(load_notes(path)[0].text, "é")


if __name__ == "__main__":
    unittest.main()
