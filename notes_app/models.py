"""Modèle de données d'une note."""
from dataclasses import dataclass, field
from datetime import datetime


def default_name(text: str, limit: int = 40) -> str:
    """Nom déduit du début du texte (première ligne, tronquée)."""
    lines = text.strip().splitlines()
    first = lines[0].strip() if lines else ""
    if len(first) > limit:
        first = first[: limit - 1].rstrip() + "…"
    return first or "(sans nom)"


@dataclass
class Note:
    text: str
    created_at: datetime
    tags: list[str] = field(default_factory=list)
    name: str = ""

    def __post_init__(self) -> None:
        # Sans nom explicite (anciennes notes comprises), on le déduit du texte.
        if not self.name.strip():
            self.name = default_name(self.text)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "text": self.text,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        return cls(
            text=data["text"],
            created_at=datetime.fromisoformat(data["created_at"]),
            tags=list(data.get("tags", [])),
            name=data.get("name", ""),
        )
