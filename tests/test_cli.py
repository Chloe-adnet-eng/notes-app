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


def run(argv, stdin=""):
    out = io.StringIO()
    with mock.patch("sys.stdin", io.StringIO(stdin)), contextlib.redirect_stdout(out):
        main(argv)
    return out.getvalue()


class ClearTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "notes.json"
        env = mock.patch.dict(os.environ, {"NOTES_FILE": str(self.path)})
        env.start()
        self.addCleanup(env.stop)
        save_notes(self.path, [
            Note(text="a", created_at=datetime(2026, 11, 1, 9, 0), tags=[]),
            Note(text="b", created_at=datetime(2026, 11, 2, 9, 0), tags=[]),
        ])

    def test_clear_yes(self):
        out = run(["clear", "--yes"])
        self.assertIn("2 notes supprimées.", out)
        self.assertEqual(load_notes(self.path), [])

    def test_clear_confirmed(self):
        out = run(["clear"], stdin="o\n")
        self.assertIn("Supprimer 2 notes ? [o/N]", out)
        self.assertEqual(load_notes(self.path), [])

    def test_clear_cancelled(self):
        for stdin in ("n\n", "\n", ""):
            with self.subTest(stdin=stdin):
                out = run(["clear"], stdin=stdin)
                self.assertIn("Annulé.", out)
                self.assertEqual(len(load_notes(self.path)), 2)

    def test_clear_without_notes(self):
        save_notes(self.path, [])
        self.assertIn("Aucune note.", run(["clear", "--yes"]))


if __name__ == "__main__":
    unittest.main()
