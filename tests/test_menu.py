import io
import unittest
from datetime import datetime
from unittest import mock

from notes_app.__main__ import choose_note, move_selection
from notes_app.models import Note


class MoveSelectionTest(unittest.TestCase):
    def test_down_goes_to_next(self):
        self.assertEqual(move_selection(0, 1, 3), 1)

    def test_up_goes_to_previous(self):
        self.assertEqual(move_selection(2, -1, 3), 1)

    def test_down_wraps_to_top(self):
        self.assertEqual(move_selection(2, 1, 3), 0)

    def test_up_wraps_to_bottom(self):
        self.assertEqual(move_selection(0, -1, 3), 2)

    def test_single_note_stays(self):
        self.assertEqual(move_selection(0, 1, 1), 0)
        self.assertEqual(move_selection(0, -1, 1), 0)


class ChooseNoteFallbackTest(unittest.TestCase):
    def setUp(self):
        self.notes = [
            Note(text="a", created_at=datetime(2026, 11, 1, 9, 0), tags=[]),
            Note(text="b", created_at=datetime(2026, 11, 2, 9, 0), tags=[]),
        ]

    def test_non_tty_uses_numbered_menu(self):
        with mock.patch("builtins.input", return_value="2"), \
                mock.patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(choose_note(self.notes), 1)

    def test_empty_answer_cancels(self):
        with mock.patch("builtins.input", return_value=""), \
                mock.patch("sys.stdout", new_callable=io.StringIO):
            self.assertIsNone(choose_note(self.notes))


if __name__ == "__main__":
    unittest.main()
