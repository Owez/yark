"""Comments information and utilities"""
# TODO: check new parent system works

from __future__ import annotations
import multiprocessing
from functools import partial
from typing import Optional, Any
from .comment_author import CommentAuthor
from .element import Element
from ..parent import Parent
import datetime


class Comment:
    parent: Parent
    id: str
    author: CommentAuthor
    body: Element
    favorited: Element
    deleted: Element
    created: datetime.datetime
    children: Comments

    @staticmethod
    def new(
        parent: Parent,
        id: str,
        author_id: str,
        author_name: str,
        author_icon_url: str,
        body: str,
        favorited: bool,
        created: datetime.datetime,
    ) -> Comment:
        """Creates a new comment with simplified information inputs"""
        # Initiate comment
        comment = Comment()

        # Make comment parent for children
        comment_parent = Parent.new_comment(parent.archive, comment)

        # Normal
        comment.parent = parent
        comment.id = id
        comment.author = CommentAuthor.new_or_update(
            Parent.new_archive(parent.archive), author_id, author_name, author_icon_url
        )
        comment.body = Element.new(comment_parent, body)
        comment.favorited = Element.new(comment_parent, favorited)
        comment.deleted = Element.new(comment_parent, False)
        comment.created = created
        comment.children = Comments(Parent.new_comment(parent.archive, comment))
        return comment

    def update(self, entry: dict[str, Any]):
        """Updates comment using new metadata schema, adding a new timestamp to any changes and also updating it's author automatically"""
        self.author.new_or_update(
            Parent.new_archive(self.parent.archive),
            entry["author_id"],
            entry["author"],
            entry["author_thumbnail"],
        )
        self.body.update(None, entry["text"])
        self.favorited.update(None, entry["is_favorited"])
        self.deleted.update(None, False)

    @staticmethod
    def _from_archive_ib(parent: Parent, id: str, element: dict) -> Comment:
        """Loads a comment from it's body dict with it's id passed in, use this as a new body"""
        # Initiate comment
        comment = Comment()

        # Make comment parent for children
        comment_parent = Parent.new_comment(parent.archive, comment)

        # Normal
        comment = Comment()
        comment.parent = parent
        comment.id = id
        comment.author = parent.archive.comment_authors[element["author_id"]]
        comment.body = Element._from_archive_o(comment_parent, element["body"])
        comment.favorited = Element._from_archive_o(
            comment_parent, element["favorited"]
        )
        comment.deleted = Element._from_archive_o(comment_parent, element["deleted"])
        comment.created = datetime.datetime.fromisoformat(element["created"])

        # Get children using the id & body method
        comment.children = Comments(comment_parent)
        for id in element["children"].keys():
            comment.children.inner[id] = Comment._from_archive_ib(
                comment.children.parent, id, element["children"][id]
            )

        # Return
        return comment

    def _to_archive_b(self) -> dict:
        """Converts comment to it's archival dict body"""
        # Get children using the id & body method
        children = {}
        for id in self.children.inner.keys():
            children[id] = self.children.inner[id]._to_archive_b()

        # Basics
        payload = {
            "author_id": self.author.id,
            "body": self.body._to_archive_o(),
            "favorited": self.favorited._to_archive_o(),
            "deleted": self.deleted._to_archive_o(),
            "created": self.created.isoformat(),
            "children": children,
        }

        # Return
        return payload


class Comments:
    parent: Parent
    inner: dict[str, Comment]

    def __init__(self, parent: Parent) -> None:
        self.parent = parent
        self.inner = {}

    def update(self, comments: list[dict]):
        """Updates comments according to metadata"""
        # All comments which have been found so we can see the difference to find deleted comments
        known: list[str] = []

        # List of comments which are children of the parent of `str`; we do this to guarantee we have all roots before we add children
        adoption_queue: list[tuple[str, Comment]] = []

        # Go through comments found using processing pool for images
        p = multiprocessing.Pool(16)
        p.map(
            partial(
                self._update_comment,
                known=known,
                adoption_queue=adoption_queue,
            ),
            comments,
        )

        # Add all the children to parents now we know they're all there
        for parent_id, comment in adoption_queue:
            # Set the parent of this child comment to the same one the children list uses (they're the same)
            parent = self.inner[parent_id].children
            comment.parent = parent.parent

            # Add this child comment into aforementioned children list
            self.inner[parent_id].children.inner[comment.id] = comment

        # Update those who have been deleted by finding the difference between recently got and archived
        for id in self.inner.keys():
            if id not in known:
                comment = self.inner[id]
                comment.deleted.update(None, True)

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
                self.parent,
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

    @staticmethod
    def _from_archive_o(parent: Parent, comments: dict[str, dict]):
        """Loads comments from a comment level in a Yark archive"""
        output = Comments(parent)
        for id in comments.keys():
            output.inner[id] = Comment._from_archive_ib(output.parent, id, comments[id])
        return output

    def _to_archive_o(self) -> dict[str, dict]:
        """Saves each comment as an id & body style dict inside of comments"""
        payload = {}
        for id in self.inner:
            payload[id] = self.inner[id]._to_archive_b()
        return payload


def _decode_comment_id(id: str) -> tuple[Optional[str], str]:
    """Decodes a comment id into it's top-level or parent and self"""
    if "." in id:
        got = id.split(".")
        return got[0], got[1]
    return None, id