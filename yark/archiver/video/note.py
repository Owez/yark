"""User note-taking/journaling to record interesting parts of videos using a timestamp"""

from __future__ import annotations
from uuid import uuid4
from typing import Optional
from ..parent import Parent


class Note:
    parent: Parent
    id: str
    timestamp: int
    title: str
    body: Optional[str]

    @staticmethod
    def new(parent: Parent, timestamp: int, title: str, body: Optional[str] = None):
        """Creates a new note"""
        note = Note()
        note.parent = parent
        note.id = str(uuid4())
        note.timestamp = timestamp
        note.title = title
        note.body = body
        return note

    @staticmethod
    def _from_archive_o(parent: Parent, element: dict) -> Note:
        """Loads existing note object dict from an archive"""
        note = Note()
        note.parent = parent
        note.id = element["id"]
        note.timestamp = element["timestamp"]
        note.title = element["title"]
        note.body = element["body"]
        return note

    def _to_archive_o(self) -> dict:
        """Converts note to it's object dict for archival"""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "title": self.title,
            "body": self.body,
        }
