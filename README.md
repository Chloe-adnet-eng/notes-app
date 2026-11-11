# notes-app

Petite application en ligne de commande pour prendre des notes et en obtenir une synthèse.
Bibliothèque standard Python uniquement (3.11+).

## Utilisation
```
python -m notes_app add "Appeler le plombier" --tags maison,urgent
python -m notes_app add "Appeler le plombier" --name "Plombier"
python -m notes_app list
python -m notes_app list --tag maison
python -m notes_app delete
python -m notes_app clear --yes
python -m notes_app summary
```
`--name` est facultatif : sans lui, le nom est déduit du début du texte.
`delete` affiche un menu numéroté avec le nom de chaque note ; une saisie vide annule.
`clear` supprime toutes les notes ; sans `--yes`, elle refuse (code de sortie 1) et explique comment relancer.
Les notes sont stockées dans `notes.json` (ou le fichier indiqué par `NOTES_FILE`).

## Tests
```
python -m unittest discover -s tests -v
```
