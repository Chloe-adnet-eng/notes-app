"""Synthèse des notes : nombre, tags les plus fréquents, notes récentes."""
from collections import Counter

from notes_app.models import Note


def filter_by_tag(notes: list[Note], tag: str) -> list[Note]:
    return [n for n in notes if tag in n.tags]


def remove_note(notes: list[Note], index: int) -> Note:
    """Retire et renvoie la note à la position donnée (0 = première)."""
    if not 0 <= index < len(notes):
        raise IndexError(f"Position de note invalide : {index}")
    return notes.pop(index)


def find_by_name(notes: list[Note], name: str) -> list[Note]:
    """Renvoie les notes dont le nom est exactement `name`."""
    return [n for n in notes if n.name == name]


def rename_note(note: Note, new_name: str) -> None:
    """Change le nom de la note ; refuse un nom vide."""
    new_name = new_name.strip()
    if not new_name:
        raise ValueError("Le nouveau nom ne peut pas être vide.")
    note.name = new_name


def top_tags(notes: list[Note], limit: int = 3) -> list[tuple[str, int]]:
    counter = Counter(tag for n in notes for tag in n.tags)
    return counter.most_common(limit)


def summarize(notes: list[Note], recent: int = 3) -> str:
    if not notes:
        return "Aucune note."
    lines = [f"{len(notes)} note(s)."]
    tags = top_tags(notes)
    if tags:
        lines.append("Tags principaux : " + ", ".join(f"{t} ({c})" for t, c in tags))
    latest = sorted(notes, key=lambda n: n.created_at, reverse=True)[:recent]
    lines.append("Dernières notes :")
    lines.extend(f"- {n.created_at:%Y-%m-%d %H:%M} {n.text}" for n in latest)
    return "\n".join(lines)
