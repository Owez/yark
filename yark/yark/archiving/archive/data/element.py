# Standard Imports
from __future__ import annotations
from typing import Any, TYPE_CHECKING
from dataclasses import dataclass, field
import datetime

# Local Imports
if TYPE_CHECKING:
    from yark.yark.archiving.archive import Archive
    from yark.archiving.archiver.video.data import Video

# External Imports


@dataclass()
class Element:
    archive: Archive
    inner: dict[datetime.datetime, Any] = field(default_factory=dict)

    @staticmethod
    def new_data(archive: Archive, data: Any) -> Element:
        """Creates a new element with some initial data inside of it"""
        return Element(archive, {datetime.datetime.utcnow(): data})

    def update(self, kind_video: tuple[str, Video] | None, data: Any) -> None:
        """Updates element if it needs to be and returns self, reports change unless `kind` is none"""
        # Check if updating is needed
        has_id = hasattr(data, "id")
        current = self.current()
        if (not has_id and current != data) or (has_id and data.id != current.id):
            # Update
            self.inner[datetime.datetime.utcnow()] = data

            # Report about a change to a video if wanted
            if kind_video is not None:
                self.archive.reporter.add_updated(kind_video[0], kind_video[1])

    def current(self) -> Any:
        """Returns most recent element"""
        return self.inner[list(self.inner.keys())[-1]]

    def changed(self) -> bool:
        """Checks if the value has ever been modified from its original state"""
        return len(self.inner) > 1

    @staticmethod
    def from_archive_o(archive: Archive, encoded: dict[str, Any]) -> Element:
        """Converts object dict from archive to this element"""
        # Basics
        element = Element(archive)

        # Inner elements
        for key in encoded:
            date = datetime.datetime.fromisoformat(key)
            element.inner[date] = encoded[key]

        return element

    def to_archive_o(self) -> dict[str, Any]:
        """Converts element to object dict for an archive"""
        # Convert each item
        encoded = {}
        for date in self.inner:
            # Convert element value if method available to support custom
            data = self.inner[date]
            data = data._to_element() if hasattr(data, "_to_element") else data

            # Add encoded data to iso-formatted string date
            encoded[date.isoformat()] = data

        return encoded
