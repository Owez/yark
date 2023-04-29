# Standard Imports
from __future__ import annotations
from typing import Any, TYPE_CHECKING
from dataclasses import dataclass
import datetime

# Local Imports
if TYPE_CHECKING:
    from yark.yark.archiving.archive import Archive
    from yark.yark.archiving.archive.data.comment_author import CommentAuthor
    from yark.yark.archiving.archive.data import Element
    from yark.yark.archiving.archive.data.video import Comments

# External Imports


@dataclass
class Comment:
    archive: Archive
    id: str
    author: CommentAuthor
    body: Element
    favorited: Element
    deleted: Element
    created: datetime.datetime
    children: Comments

    @staticmethod
    def new(
        archive: Archive,
        id: str,
        author_id: str,
        author_name: str,
        author_icon_url: str,
        body: str,
        favorited: bool,
        created: datetime.datetime,
    ) -> Comment:
        """Creates a new comment with simplified information inputs"""
        return Comment(
            archive,
            id,
            CommentAuthor.new_or_update(
                archive, author_id, author_name, author_icon_url
            ),
            Element.new_data(archive, body),
            Element.new_data(archive, favorited),
            Element.new_data(archive, False),
            created,
            Comments(archive),
        )

    def update(self, entry: dict[str, Any]) -> None:
        """Updates comment using new metadata schema, adding a new timestamp to any changes and
         also updating its author automatically"""
        self.author.new_or_update(
            self.archive,
            entry["author_id"],
            entry["author"],
            entry["author_thumbnail"],
        )
        self.body.update(None, entry["text"])
        self.favorited.update(None, entry["is_favorited"])
        self.deleted.update(None, False)


def _from_archive_ib(archive: Archive, kind: str, element: dict[str, Any]) -> Comment:
    """Loads a comment from its body dict with its id passed in, use this as a new body"""

    # Get children using the id & body method
    children = Comments(archive)
    for kind in element["children"].keys():
        children.inner[kind] = Comment._from_archive_ib(
            archive, kind, element["children"][kind]
        )

    comment = Comment(
        archive,
        kind,
        archive.comment_authors[element["author_id"]],
        Element.from_archive_o(archive, element["body"]),
        Element.from_archive_o(archive, element["favorited"]),
        Element.from_archive_o(archive, element["deleted"]),
        datetime.datetime.fromisoformat(element["created"]),
        children,
    )

    return comment


def _to_archive_b(comment: Comment) -> dict[str, Any]:
    """Converts comment to it's archival dict body"""
    # Get children using the id & body method
    children = {}
    for kind in comment.children.inner.keys():
        children[kind] = comment.children.inner[kind]._to_archive_b()

    payload = {
        "author_id": comment.author.id,
        "body": comment.body.to_archive_o(),
        "favorited": comment.favorited.to_archive_o(),
        "deleted": comment.deleted.to_archive_o(),
        "created": comment.created.isoformat(),
        "children": children,
    }

    return payload

