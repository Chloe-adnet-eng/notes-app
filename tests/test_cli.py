import contextlib
import io
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

from notes_app.__main__ import main
from notes_app.models import Note
from notes_app.store import load_notes, save_notes


class ClearCommandTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "notes.json"
        patcher = mock.patch.dict(os.environ, {"NOTES_FILE": str(self.path)})
        patcher.start()
        self.addCleanup(patcher.stop)
        save_notes(self.path, [
            Note(text="a", created_at=datetime(2026, 11, 1, 9, 0), tags=[]),
            Note(text="b", created_at=datetime(2026, 11, 2, 9, 0), tags=[]),
        ])

    def run_main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = None
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                main(list(argv))
            except SystemExit as e:
                code = e.code
        return code, out.getvalue(), err.getvalue()

    def test_clear_without_yes_refuses(self):
        code, out, err = self.run_main("clear")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("--yes", err)
        self.assertEqual(len(load_notes(self.path)), 2)

    def test_clear_with_yes_empties_notes(self):
        code, out, _ = self.run_main("clear", "--yes")
        self.assertIsNone(code)
        self.assertIn("2", out)
        self.assertEqual(load_notes(self.path), [])

    def test_clear_with_no_notes_does_not_require_yes(self):
        save_notes(self.path, [])
        code, out, _ = self.run_main("clear")
        self.assertIsNone(code)
        self.assertEqual(out.strip(), "Aucune note.")


class AddDuplicateNameTest(unittest.TestCase):
    run_main = ClearCommandTest.run_main

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "notes.json"
        patcher = mock.patch.dict(os.environ, {"NOTES_FILE": str(self.path)})
        patcher.start()
        self.addCleanup(patcher.stop)
        save_notes(self.path, [
            Note(text="x", created_at=datetime(2026, 11, 1, 9, 0), name="Courses"),
        ])

    def test_duplicate_name_refused(self):
        code, out, err = self.run_main("add", "autre", "--name", "Courses")
        self.assertEqual(code, 1)
        self.assertIn("Courses", err)
        self.assertEqual(len(load_notes(self.path)), 1)

    def test_duplicate_name_refused_ignoring_case_and_spaces(self):
        code, _, _ = self.run_main("add", "autre", "--name", "  courses ")
        self.assertEqual(code, 1)
        self.assertEqual(len(load_notes(self.path)), 1)

    def test_derived_name_duplicate_refused(self):
        self.run_main("add", "Idée géniale")
        code, _, _ = self.run_main("add", "idée géniale\nsuite")
        self.assertEqual(code, 1)
        self.assertEqual(len(load_notes(self.path)), 2)

    def test_distinct_name_accepted(self):
        code, _, _ = self.run_main("add", "autre", "--name", "Travail")
        self.assertIsNone(code)
        self.assertEqual(len(load_notes(self.path)), 2)


if __name__ == "__main__":
    unittest.main()
