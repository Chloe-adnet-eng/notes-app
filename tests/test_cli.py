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


class TodayCommandTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "notes.json"
        patcher = mock.patch.dict(os.environ, {"NOTES_FILE": str(self.path)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_main(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main(list(argv))
        return out.getvalue()

    def test_today_summarizes_only_todays_notes(self):
        save_notes(self.path, [
            Note(text="ancienne", created_at=datetime(2020, 1, 1, 9, 0), tags=["vieux"]),
            Note(text="du jour", created_at=datetime.now(), tags=["neuf"]),
        ])
        out = self.run_main("today")
        self.assertIn("1 note(s).", out)
        self.assertIn("du jour", out)
        self.assertIn("neuf", out)
        self.assertNotIn("ancienne", out)
        self.assertNotIn("vieux", out)

    def test_today_without_notes_of_the_day(self):
        save_notes(self.path, [
            Note(text="ancienne", created_at=datetime(2020, 1, 1, 9, 0)),
        ])
        self.assertEqual(self.run_main("today").strip(), "Aucune note aujourd'hui.")


class SearchCommandTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "notes.json"
        patcher = mock.patch.dict(os.environ, {"NOTES_FILE": str(self.path)})
        patcher.start()
        self.addCleanup(patcher.stop)
        save_notes(self.path, [
            Note(text="Appeler le plombier", created_at=datetime(2026, 11, 1, 9, 0), tags=["maison"]),
            Note(text="Acheter du pain", created_at=datetime(2026, 11, 2, 9, 0)),
        ])

    def run_main(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main(list(argv))
        return out.getvalue()

    def test_search_prints_matching_notes(self):
        out = self.run_main("search", "PLOMBIER")
        self.assertIn("Appeler le plombier", out)
        self.assertIn("[maison]", out)
        self.assertNotIn("pain", out)

    def test_search_without_result(self):
        out = self.run_main("search", "zzz")
        self.assertEqual(out.strip(), "Aucune note trouvée.")


if __name__ == "__main__":
    unittest.main()
