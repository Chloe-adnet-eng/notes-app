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
    delete = sub.add_parser("delete", help="supprimer une note par son numéro")
    delete.add_argument("number", type=int, help="numéro de la note (voir `list`), à partir de 1")
    delete.add_argument("--yes", action="store_true", help="confirme la suppression")
    clear = sub.add_parser("clear", help="supprimer toutes les notes")
    clear.add_argument("--yes", action="store_true", help="confirme la suppression de toutes les notes")
    sub.add_parser("summary", help="synthèse des notes")
    return parser


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
        if not 1 <= args.number <= len(notes):
            print(
                f"Numéro invalide : {args.number} (il y a {len(notes)} note(s), "
                "numérotées à partir de 1).",
                file=sys.stderr,
            )
            sys.exit(1)
        if not args.yes:
            print(
                f"Refus : cette commande supprime la note {args.number} ({notes[args.number - 1].name}). "
                f"Relance avec --yes pour confirmer : python -m notes_app delete {args.number} --yes",
                file=sys.stderr,
            )
            sys.exit(1)
        remove_note(notes, args.number - 1)
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
            number = next(i for i, other in enumerate(notes, start=1) if other is n)
            tags = f" [{', '.join(n.tags)}]" if n.tags else ""
            print(f"{number}. {n.created_at:%Y-%m-%d %H:%M} {n.name} : {n.text}{tags}")
    elif args.command == "summary":
        print(summarize(notes))


if __name__ == "__main__":
    main()
