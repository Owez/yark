from __future__ import annotations
from .element import Element
from .image import Image
from typing import TYPE_CHECKING
from ..parent import Parent

if TYPE_CHECKING:
    from ..archive import Archive


IMAGE_AUTHOR_ICON = "jpg"
"""Image extension setting for all author icons"""


class CommentAuthor:
    parent: Parent
    id: str
    name: Element
    icon: Element

    @staticmethod
    def new_or_update(
        parent: Parent, id: str, name: str, icon_url: str
    ) -> CommentAuthor:
        """Adds a new author with `name` of `id` if it doesn't exist, or tries to update `name` if it does"""
        # Try to get from archive
        author = parent.archive.comment_authors.get(id)

        # Create new if it's not there
        if author is None:
            author = CommentAuthor()
            author.parent = parent
            author.id = id
            author.name = Element.new(author, name)
            author.icon = Element.new(
                author, Image.new(author, icon_url, IMAGE_AUTHOR_ICON)
            )
            parent.archive.comment_authors[id] = author

        # Update existing
        else:
            author.name.update(None, name)
            author.icon.update(None, Image.new(author, icon_url, IMAGE_AUTHOR_ICON))

        # Return
        return author

    @staticmethod
    def _from_archive_ib(parent: Parent, id: str, element: dict) -> CommentAuthor:
        """Decodes comment author from the body dict and adds the id passed in from an archive"""
        author = CommentAuthor()
        author.parent = parent
        author.id = id
        author.name = Element._from_archive_o(element["name"], author)
        author.icon = Element._from_archive_o(element["icon"], author)
        return author

    def _to_archive_b(self) -> dict:
        """Encodes comment author to it's dict body for an archive"""
        return {"name": self.name._to_archive_o(), "icon": self.icon._to_archive_o()}
