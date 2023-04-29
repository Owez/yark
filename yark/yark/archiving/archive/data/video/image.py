# Standard Imports
from __future__ import annotations
from typing import TYPE_CHECKING, Any
from pathlib import Path
from dataclasses import dataclass
import hashlib

# Local Imports
from yark.yark.archiving.archive.data.element import Element

if TYPE_CHECKING:
    from yark.yark.archiving.archive.data import Archive


# External Imports
import requests


@dataclass
class Image:
    archive: Archive
    id: str
    path: Path
    ext: str

    @staticmethod
    def new(archive: Archive, url: str, ext: str) -> Image:
        """Pulls a new image from YouTube and saves"""
        # Get image and id which is a hash
        downloaded_image, id = _image_and_hash(url)

        # Calculate path
        path = _path(archive, id, ext)

        # Save to collection
        with open(path, "wb+") as file:
            file.write(downloaded_image)

        return Image(archive, id, path, ext)

    @staticmethod
    def load(archive: Archive, id: str, ext: str) -> Image:
        """Loads existing image from saved path by id"""
        path = _path(archive, id, ext) / f"{id}.{ext}"
        return Image(archive, id, path, ext)

    def _to_element(self) -> str:
        """Converts images instance to value used for element identification"""
        return self.id


def image_element_from_archive(
    archive: Archive, element: dict[str, Any], ext: str
) -> Element:
    """Helper function to convert a dict-based element containing images to properly formed element"""
    decoded = Element.from_archive_o(archive, element)
    for date in decoded.inner:
        decoded.inner[date] = Image.load(archive, decoded.inner[date], ext)
    return decoded


def _image_and_hash(url: str) -> tuple[bytes, str]:
    """Downloads an image and calculates it's BLAKE2 hash, returning both"""
    image = requests.get(url).content
    hash = hashlib.blake2b(image, digest_size=20, usedforsecurity=False).hexdigest()
    return image, hash


def _path(archive: Archive, kind: str, ext: str) -> Path:
    """Returns path to image based on context"""
    return archive.path / "images" / f"{kind}.{ext}"
