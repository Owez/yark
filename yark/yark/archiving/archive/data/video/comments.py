"""Comments information and utilities"""
# Standard Imports
from __future__ import annotations
from typing import Optional, Any, TYPE_CHECKING
from dataclasses import dataclass, field
import datetime

# Local Imports
if TYPE_CHECKING:
    from yark.yark.archiving.archive import Archive
    from yark.archiving.archive.data.video import Comment

# External Imports


@dataclass
class Comments:
    archive: Archive
    inner: dict[str, Comment] = field(default_factory=dict)

    def update(self, comments: list[dict[str, Any]]) -> None:
        """Updates comments according to metadata"""
        # All comments identifiers which have been found so we can see the difference to find deleted comments
        known: list[str] = []

        # Adoption queue for comments under a parent id
        to_adopt: list[tuple[str, Comment]] = []

        # Go through comments found
        for comment in comments:
            known.append(comment["id"])
            possible_child = self._update_comment(comment)
            if possible_child:
                to_adopt.append(possible_child)

        # Add all child comments to their parents now that we know roots have been resolved
        for parent_id, child_comment in to_adopt:
            self.inner[parent_id].children.inner[child_comment.id] = child_comment

        # Update those who have been deleted by finding the difference between recently got and archived
        # NOTE: could do set intersection?
        for id in self.inner.keys():
            if id not in known:
                deleted_comment = self.inner[id]
                deleted_comment.deleted.update(None, True)

    def _update_comment(self, entry: dict[str, Any]) -> tuple[str, Comment] | None:
        """Adds or update the comment from metadata provided in `entry`,
         returning its parent id and parsed comment if it couldn't be added to the root"""
        # Decode the comment's identifier and parent identifier
        parent_id, id = _decode_comment_id(entry["id"])

        # Get the comment from root or from a child
        comment = self.inner.get(id if parent_id is None else parent_id)
        if parent_id is not None and comment is not None:
            comment = comment.children.inner.get(id)

        # Create a new one if it couldn't be found
        if comment is None:
            # Make the new comment class
            timestamp = datetime.datetime.fromtimestamp(entry["timestamp"])
            comment = Comment.new(
                self.archive,
                entry["id"],
                entry["author_id"],
                entry["author"],
                entry["author_thumbnail"],
                entry["text"],
                entry["is_favorited"],
                timestamp,
            )

            # Return comment to process more because it's a child
            if parent_id is not None:
                return parent_id, comment

            # Add straight to root
            self.inner[comment.id] = comment

        # Update the existing comment
        else:
            comment.update(entry)

        # Return nothing if it's been added to the root
        return None

    def empty(self) -> bool:
        """Returns if there are any comments or not"""
        return len(self.inner) == 0

    def paginate(self, page: int, items: int = 50) -> list[Comment]:
        """Paginates comments stored by a `page` of length `items`"""
        start = (page - 1) * items
        if start > len(self.inner.keys()):
            return []
        return list(self.inner.values())[start : start + items]

    '''
    def _update_comment(
        self,
        entry: dict,
        known: list[str],
        adoption_queue: list[tuple[str, Comment]],
    ):
        """Runs through the complete update procedures for one comment"""
        # Decode the identifier and possible parent; can be used to check parent
        parent_id, id = _decode_comment_id(entry["id"])

        # Add to known comments to find difference later
        known.append(id)

        # Try to update comment if it's a child
        if (
            parent_id is not None
            and parent_id in self.inner
            and id in self.inner[parent_id].children.inner
        ):
            comment = self.inner[parent_id].children.inner[id]
            comment.update(entry)

        # Try to update comment if it's a parent
        elif id in self.inner:
            comment = self.inner[id]
            comment.update(entry)

        # Create a new comment
        else:
            # Encode into a full comment with no parent no matter what
            created = datetime.datetime.fromtimestamp(entry["timestamp"])
            comment = Comment.new(
                self.archive,
                id,
                entry["author_id"],
                entry["author"],
                entry["author_thumbnail"],
                entry["text"],
                entry["is_favorited"],
                created,
            )

            # Add comment to our comments
            if parent_id is None:
                self.inner[id] = comment

            # Add to adoption queue if the comment is a child
            else:
                adoption_queue.append((parent_id, comment))
    '''


def from_archive_o(archive: Archive, comments: dict[str, dict[str, Any]]) -> Comments:
    """Loads comments from a comment level in a Yark archive"""
    output = Comments(archive)
    for kind in comments.keys():
        output.inner[kind] = Comment._from_archive_ib(archive, kind, comments[kind])

    return output


def _to_archive_o(self) -> dict[str, dict[str, Any]]:
    """Saves each comment as an id & body style dict inside of comments"""
    payload = {}
    for kind in self.inner:
        payload[kind] = self.inner[kind]._to_archive_b()
    return payload


def _decode_comment_id(kind: str) -> tuple[Optional[str], str]:
    """Decodes a comment id into it's top-level or parent and self"""
    if "." in kind:
        got = kind.split(".")
        return got[0], got[1]

    return None, kind
