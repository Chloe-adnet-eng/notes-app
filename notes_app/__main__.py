"""Interface en ligne de commande : add, list, delete, summary."""
import argparse
import sys
from datetime import datetime

from notes_app.models import Note
from notes_app.store import load_notes, notes_path, save_notes
from notes_app.summary import filter_by_tag, remove_note, summarize


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="notes_app")
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add", help="ajouter une note")
    add.add_argument("text")
    add.add_argument("--tags", default="", help="tags séparés par des virgules")
    add.add_argument("--name", default="", help="nom de la note (par défaut : début du texte)")
    lst = sub.add_parser("list", help="lister les notes")
    lst.add_argument("--tag")
    sub.add_parser("delete", help="supprimer une note via un menu")
    clear = sub.add_parser("clear", help="supprimer toutes les notes")
    clear.add_argument("--yes", action="store_true", help="confirme la suppression de toutes les notes")
    sub.add_parser("summary", help="synthèse des notes")
    return parser


def format_note_line(index: int, note: Note, excerpt_limit: int = 40) -> str:
    """Ligne de menu : numéro, nom, date et extrait du texte."""
    excerpt = " ".join(note.text.split())
    if len(excerpt) > excerpt_limit:
        excerpt = excerpt[: excerpt_limit - 1].rstrip() + "…"
    return f"{index}. {note.name} ({note.created_at:%Y-%m-%d %H:%M}) {excerpt}"


def name_exists(notes: list[Note], name: str) -> bool:
    """Vrai si une note porte déjà ce nom (casse et espaces alentour ignorés)."""
    wanted = name.strip().casefold()
    return any(n.name.strip().casefold() == wanted for n in notes)


def move_selection(current: int, delta: int, count: int) -> int:
    """Déplace la sélection de `delta` positions en bouclant aux extrémités."""
    return (current + delta) % count


def _curses_menu(stdscr, notes: list[Note]) -> int | None:
    import curses

    curses.curs_set(0)
    stdscr.keypad(True)
    current = 0
    top = 0
    while True:
        height, width = stdscr.getmaxyx()
        visible = max(1, height - 2)
        if current < top:
            top = current
        elif current >= top + visible:
            top = current - visible + 1
        stdscr.erase()
        stdscr.addnstr(0, 0, "↑/↓ pour choisir, Entrée pour supprimer, q/Échap pour annuler",
                       max(0, width - 1))
        for row, i in enumerate(range(top, min(len(notes), top + visible)), start=1):
            attr = curses.A_REVERSE if i == current else curses.A_NORMAL
            stdscr.addnstr(row, 0, format_note_line(i + 1, notes[i]), max(0, width - 1), attr)
        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_UP:
            current = move_selection(current, -1, len(notes))
        elif key == curses.KEY_DOWN:
            current = move_selection(current, 1, len(notes))
        elif key in (curses.KEY_ENTER, 10, 13):
            return current
        elif key in (ord("q"), 27):
            return None


def _numbered_menu(notes: list[Note]) -> int | None:
    for i, n in enumerate(notes, start=1):
        print(format_note_line(i, n))
    while True:
        try:
            answer = input("Numéro de la note à supprimer (vide pour annuler) : ").strip()
        except EOFError:
            return None
        if not answer:
            return None
        if answer.isdigit() and 1 <= int(answer) <= len(notes):
            return int(answer) - 1
        print("Choix invalide.")


def choose_note(notes: list[Note]) -> int | None:
    """Affiche le menu et renvoie la position choisie, ou None si annulé.

    Menu à flèches via curses dans un vrai terminal ; sinon menu numéroté.
    """
    if sys.stdin.isatty() and sys.stdout.isatty():
        try:
            import curses
        except ImportError:
            return _numbered_menu(notes)
        import os
        os.environ.setdefault("ESCDELAY", "25")
        return curses.wrapper(_curses_menu, notes)
    return _numbered_menu(notes)


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    path = notes_path()
    notes = load_notes(path)
    if args.command == "add":
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
        note = Note(text=args.text, created_at=datetime.now(), tags=tags, name=args.name)
        if name_exists(notes, note.name):
            print(f"Refus : une note nommée « {note.name} » existe déjà. "
                  "Choisis un autre nom avec --name.", file=sys.stderr)
            sys.exit(1)
        notes.append(note)
        save_notes(path, notes)
        print("Note ajoutée.")
    elif args.command == "delete":
        if not notes:
            print("Aucune note.")
            return
        index = choose_note(notes)
        if index is None:
            print("Annulé.")
            return
        remove_note(notes, index)
        save_notes(path, notes)
        print("Note supprimée.")
    elif args.command == "clear":
        if not notes:
            print("Aucune note.")
            return
        if not args.yes:
            print(
                f"Refus : cette commande supprime les {len(notes)} notes. "
                "Relance avec --yes pour confirmer : python -m notes_app clear --yes",
                file=sys.stderr,
            )
            sys.exit(1)
        save_notes(path, [])
        print(f"{len(notes)} note(s) supprimée(s).")
    elif args.command == "list":
        shown = filter_by_tag(notes, args.tag) if args.tag else notes
        for n in shown:
            tags = f" [{', '.join(n.tags)}]" if n.tags else ""
            print(f"{n.created_at:%Y-%m-%d %H:%M} {n.name} : {n.text}{tags}")
    elif args.command == "summary":
        print(summarize(notes))


if __name__ == "__main__":
    main()
