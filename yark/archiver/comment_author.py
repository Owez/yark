from __future__ import annotations
from .element import Element
from .video.image import Image
from ..utils import IMAGE_AUTHOR_ICON
from typing import TYPE_CHECKING, Any
from dataclasses import dataclass

if TYPE_CHECKING:
    from .archive import Archive


@dataclass(init=False)
class CommentAuthor:
    archive: Archive
    id: str
    name: Element
    icon: Element

    def __init__(
        self,
        archive: Archive,
        id: str,
        name_data: str | None = None,
        icon_data: Image | None = None,
    ) -> None:
        self.archive = archive
        self.id = id
        self.name = (
            Element(archive)
            if name_data is None
            else Element.new_data(archive, name_data)
        )
        self.icon = (
            Element(archive)
            if icon_data is None
            else Element.new_data(archive, icon_data)
        )

    @staticmethod
    def new_or_update(
        archive: Archive, id: str, name: str, icon_url: str
    ) -> CommentAuthor:
        """Adds a new author with `name` of `id` if it doesn't exist, or tries to update `name` if it does"""
        # Try to get from archive
        author = archive.comment_authors.get(id)

        # Create new if it's not there
        if author is None:
            # Initiate comment author
            icon = Image.new(archive, icon_url, IMAGE_AUTHOR_ICON)
            author = CommentAuthor(archive, id, name, icon)

            # Add comment author
            archive.comment_authors[id] = author

        # Update existing
        else:
            author.name.update(None, name)
            author.icon.update(
                None,
                Image.new(
                    archive,
                    icon_url,
                    IMAGE_AUTHOR_ICON,
                ),
            )

        # Return
        return author

    @staticmethod
    def _from_archive_ib(
        archive: Archive, id: str, element: dict[str, Any]
    ) -> CommentAuthor:
        """Decodes comment author from the body dict and adds the id passed in from an archive"""
        raise NotImplementedError()  # TODO: load this and image

    def _to_archive_b(self) -> dict[str, Any]:
        """Encodes comment author to it's dict body for an archive"""
        return {"name": self.name._to_archive_o(), "icon": self.icon._to_archive_o()}
