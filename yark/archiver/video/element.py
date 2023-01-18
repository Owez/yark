from __future__ import annotations
import datetime
from typing import Any, Optional, TYPE_CHECKING
from .video import Video

if TYPE_CHECKING:
    from ..archive import Archive


class Element:
    archive: Archive
    inner: dict[datetime.datetime, Any]

    @staticmethod
    def new(archive: Archive, data: Any):
        """Creates new element attached with some initial data"""
        element = Element()
        element.archive = archive
        element.inner = {datetime.datetime.utcnow(): data}
        return element

    def update(self, kind_video: Optional[tuple[str, Video]], data: Any):
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

    def current(self):
        """Returns most recent element"""
        return self.inner[list(self.inner.keys())[-1]]

    def changed(self) -> bool:
        """Checks if the value has ever been modified from it's original state"""
        return len(self.inner) > 1

    @staticmethod
    def _from_archive_o(archive: Archive, encoded: dict) -> Element:
        """Converts object dict from archive to this element"""
        # Basics
        element = Element()
        element.archive = archive
        element.inner = {}

        # Inner elements
        for key in encoded:
            date = datetime.datetime.fromisoformat(key)
            element.inner[date] = encoded[key]

        # Return
        return element

    def _to_archive_o(self) -> dict:
        """Converts element to object dict for an archive"""
        # Convert each item
        encoded = {}
        for date in self.inner:
            # Convert element value if method available to support custom
            data = self.inner[date]
            data = data._to_element() if hasattr(data, "_to_element") else data

            # Add encoded data to iso-formatted string date
            encoded[date.isoformat()] = data

        # Return
        return encoded
