"""Modèle de données d'une note."""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Note:
    text: str
    created_at: datetime
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"text": self.text, "created_at": self.created_at.isoformat(), "tags": self.tags}

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        return cls(
            text=data["text"],
            created_at=datetime.fromisoformat(data["created_at"]),
            tags=list(data.get("tags", [])),
        )
