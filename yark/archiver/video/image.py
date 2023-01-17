from __future__ import annotations
from pathlib import Path
from .element import Element
import requests
import hashlib
from ..parent import Parent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .video import Video
    from .comment_author import CommentAuthor


class Image:
    parent: "Video" | "CommentAuthor"
    id: str
    path: Path
    ext: str

    @staticmethod
    def new(parent: "Video" | "CommentAuthor", url: str, ext: str) -> Image:
        """Pulls a new image from YouTube and saves"""
        # Basic details
        image = Image()
        image.parent = parent
        image.ext = ext

        # Get image and id which is a hash
        downloaded_image, image.id = _image_and_hash(url)

        # Calculate path
        image.path = image._path()

        # Save to collection
        with open(image.path, "wb+") as file:
            file.write(downloaded_image)

        # Return
        return image

    def _path(self) -> Path:
        """Returns path to current image"""
        return self.parent.archive.path / "images" / f"{self.id}.{self.ext}"

    @staticmethod
    def load(id: str, parent: "Video" | "CommentAuthor", ext: str):
        """Loads existing image from saved path by id"""
        image = Image()
        image.id = id
        image.parent = parent
        image.ext = ext
        image.path = image._path() / f"{image.id}.{ext}"
        return image

    @staticmethod
    def _from_element(element: dict, video: "Video", ext: str) -> Element:
        """Converts element of images to properly formed images"""
        decoded = Element._from_archive_o(element, video)
        for date in decoded.inner:
            decoded.inner[date] = Image.load(decoded.inner[date], video, ext)
        return decoded

    def _to_element(self) -> str:
        """Converts images instance to value used for element identification"""
        return self.id


def _image_and_hash(url: str) -> tuple[bytes, str]:
    """Downloads an image and calculates it's BLAKE2 hash, returning both"""
    image = requests.get(url).content
    hash = hashlib.blake2b(image, digest_size=20, usedforsecurity=False).hexdigest()
    return image, hash
