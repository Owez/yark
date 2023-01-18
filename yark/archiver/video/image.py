from __future__ import annotations
from pathlib import Path
import requests
import hashlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..archive import Archive


class Image:
    archive: Archive
    id: str
    path: Path
    ext: str

    @staticmethod
    def new(archive: Archive, url: str, ext: str) -> Image:
        """Pulls a new image from YouTube and saves"""
        # Basic details
        image = Image()
        image.archive = archive
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
        return self.archive.path / "images" / f"{self.id}.{self.ext}"

    @staticmethod
    def load(archive: Archive, id: str, ext: str):
        """Loads existing image from saved path by id"""
        image = Image()
        image.archive = archive
        image.id = id
        image.ext = ext
        image.path = image._path() / f"{image.id}.{ext}"
        return image

    def _to_element(self) -> str:
        """Converts images instance to value used for element identification"""
        return self.id


def _image_and_hash(url: str) -> tuple[bytes, str]:
    """Downloads an image and calculates it's BLAKE2 hash, returning both"""
    image = requests.get(url).content
    hash = hashlib.blake2b(image, digest_size=20, usedforsecurity=False).hexdigest()
    return image, hash
