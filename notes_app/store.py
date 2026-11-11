"""Persistance des notes dans un fichier JSON."""
import json
import os
from pathlib import Path

from notes_app.models import Note

DEFAULT_FILE = "notes.json"


def notes_path() -> Path:
    return Path(os.environ.get("NOTES_FILE", DEFAULT_FILE))


def load_notes(path: Path) -> list[Note]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [Note.from_dict(d) for d in json.load(f)]


def save_notes(path: Path, notes: list[Note]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump([n.to_dict() for n in notes], f, ensure_ascii=False, indent=2)
