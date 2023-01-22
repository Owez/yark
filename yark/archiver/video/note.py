"""User note-taking/journaling to record interesting parts of videos using a timestamp"""

from __future__ import annotations
from uuid import uuid4
from typing import Optional, TYPE_CHECKING, Any
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from .video import Video


def _id_generator() -> str:
    """Generates an identifier for new notes"""
    return str(uuid4())


@dataclass
class Note:
    parent: Video
    timestamp: int
    title: str

    id: str = field(default_factory=_id_generator)
    body: Optional[str] = None

    @staticmethod
    def _from_archive_o(parent: Video, element: dict[str, Any]) -> Note:
        """Loads existing note object dict from an archive"""
        return Note(
            parent,
            element["timestamp"],
            element["title"],
            element["id"],
            element["body"],
        )

    def _to_archive_o(self) -> dict[str, Any]:
        """Converts note to it's object dict for archival"""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "title": self.title,
            "body": self.body,
        }
