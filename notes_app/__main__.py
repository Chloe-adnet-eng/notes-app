"""Interface en ligne de commande : add, list, delete, edit, clear, summary."""
import argparse
import sys
from datetime import datetime

from notes_app.models import Note
from notes_app.store import load_notes, notes_path, save_notes
from notes_app.summary import filter_by_tag, remove_note, summarize, update_note_text


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
    edit = sub.add_parser("edit", help="modifier le texte d'une note")
    edit.add_argument("number", type=int, help="numéro de la note (à partir de 1, comme dans le menu de delete)")
    edit.add_argument("text", help="nouveau texte")
    clear = sub.add_parser("clear", help="supprimer toutes les notes")
    clear.add_argument("--yes", action="store_true", help="confirme la suppression de toutes les notes")
    sub.add_parser("summary", help="synthèse des notes")
    return parser


def choose_note(notes: list[Note]) -> int | None:
    """Affiche le menu et renvoie la position choisie, ou None si annulé."""
    for i, n in enumerate(notes, start=1):
        print(f"{i}. {n.name}")
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


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    path = notes_path()
    notes = load_notes(path)
    if args.command == "add":
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
        notes.append(Note(text=args.text, created_at=datetime.now(), tags=tags, name=args.name))
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
    elif args.command == "edit":
        try:
            update_note_text(notes, args.number - 1, args.text)
        except IndexError:
            print(f"Numéro de note invalide : {args.number}.", file=sys.stderr)
            sys.exit(1)
        save_notes(path, notes)
        print("Note modifiée.")
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
