# Standard Imports
from __future__ import annotations
from typing import TYPE_CHECKING, Any
from dataclasses import dataclass

# Local Imports
from yark.yark.archiving.archive.data.element import Element
from yark.yark.archiving.archive.data.video.image import Image
from yark.yark.archiving.archive.data.video.image import image_element_from_archive
from yark.yark.utils import IMAGE_AUTHOR_ICON

if TYPE_CHECKING:
    from yark.yark.archiving.archive import Archive


# External Imports


@dataclass
class CommentAuthor:
    archive: Archive
    id: str
    name: Element
    icon: Element

    @staticmethod
    def new_or_update(archive: Archive, kind: str, name: str, icon_url: str) -> CommentAuthor:
        """Adds a new author with `name` of `id` if it doesn't exist, or tries to update `name` if it does"""
        # Try to get from archive
        author = archive.comment_authors.get(kind)

        # Create new if it's not there
        if author is None:
            # Initiate comment author
            icon = Image.new(archive, icon_url, IMAGE_AUTHOR_ICON)
            author = CommentAuthor(
                archive,
                kind,
                Element.new_data(archive, name),
                Element.new_data(archive, icon),
            )

            # Add comment author
            archive.comment_authors[kind] = author

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

        return author


def from_archive_ib(archive: Archive, kind: str, element: dict[str, Any]) -> CommentAuthor:
    """Decodes comment author from the body dict and adds the id passed in from an archive"""
    return CommentAuthor(
        archive,
        kind,
        Element.from_archive_o(archive, element["name"]),
        image_element_from_archive(archive, element["icon"], IMAGE_AUTHOR_ICON),
    )


def _to_archive_b(comment_author: CommentAuthor) -> dict[str, Any]:
    """Encodes comment author to its dict body for an archive"""
    return {"name": comment_author.name.to_archive_o(), "icon": comment_author.icon.to_archive_o()}
