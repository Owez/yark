"""Playlist archiving for channels, including links back to videos"""

from __future__ import annotations
from dataclasses import dataclass
from .archive import Archive
from enum import Enum
from .element import Element
from typing import Any


class PlaylistItemKind(Enum):
    VIDEO = 1
    LIVESTREAM = 2
    SHORT = 3


@dataclass
class PlaylistItem:
    archive: Archive
    kind: PlaylistItemKind
    id: str
    deleted: Element

    @staticmethod
    def _from_archive_o(archive: Archive, entry: dict[str, Any]) -> PlaylistItem:
        """Converts archive object dict into a class-based playlist item"""
        return PlaylistItem(
            archive,
            PlaylistItemKind(entry["kind"]),
            entry["id"],
            Element._from_archive_o(archive, entry["deleted"]),
        )

    def _to_archive_o(self) -> dict[str, Any]:
        """Converts this object to a dict to be stored in the archive"""
        return {
            "kind": self.kind.value,
            "id": self.id,
            "deleted": self.deleted._to_archive_o(),
        }


@dataclass
class Playlist:
    archive: Archive
    id: str
    videos: list[PlaylistItem]
    deleted: Element

    @staticmethod
    def _from_archive_o(archive: Archive, entry: dict[str, Any]) -> Playlist:
        """Converts archive object dict into a class-based playlist as a whole"""
        return Playlist(
            archive,
            entry["id"],
            [PlaylistItem._from_archive_o(archive, i) for i in entry["videos"]],
            Element._from_archive_o(archive, entry["deleted"]),
        )

    def _to_archive_o(self) -> dict[str, Any]:
        """Converts this object to a dict to be stored in the archive"""
        return {
            "id": self.id,
            "videos": [i._to_archive_o() for i in self.videos],
            "deleted": self.deleted._to_archive_o(),
        }
