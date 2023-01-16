from __future__ import annotations
import datetime
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .video import Video
    from .comments import Comment
    from ..archive import Archive
    from .comment_author import CommentAuthor


class Element:
    parent: "Video" | "Comment" | "Archive" | "CommentAuthor"
    inner: dict[datetime.datetime, Any]

    @staticmethod
    def new(parent: "Video" | "Comment" | "Archive" | "CommentAuthor", data):
        """Creates new element attached to a video with some initial data"""
        element = Element()
        element.parent = parent
        element.inner = {datetime.datetime.utcnow(): data}
        return element

    def update(self, kind: Optional[str], data):
        """Updates element if it needs to be and returns self, reports change unless `kind` is none"""
        # Check if updating is needed
        has_id = hasattr(data, "id")
        current = self.current()
        if (not has_id and current != data) or (has_id and data.id != current.id):
            # Update
            self.inner[datetime.datetime.utcnow()] = data

            # Report if wanted
            if kind is not None:
                archive = (
                    self.parent.archive
                    if isinstance(self.parent, Video)
                    or isinstance(self.parent, Comment)
                    or isinstance(self.parent, CommentAuthor)
                    else self.parent  # NOTE: this can be simplified but Archive would be a circular dep
                )
                archive.reporter.add_updated(kind, self)

        # Return self
        return self

    def current(self):
        """Returns most recent element"""
        return self.inner[list(self.inner.keys())[-1]]

    def changed(self) -> bool:
        """Checks if the value has ever been modified from it's original state"""
        return len(self.inner) > 1

    @staticmethod
    def _from_archive_o(
        encoded: dict, parent: "Video" | "Comment" | "Archive" | "CommentAuthor"
    ) -> Element:
        """Converts object dict from archive to this element"""
        # Basics
        element = Element()
        element.parent = parent
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
