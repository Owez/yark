# Standard Imports
from pathlib import Path
from typing import Any

# Local Imports
from yark.yark.archiving.archive.data.video.videos import Videos
from yark.yark.archiving.archive.data import comment_author
from yark.yark.archiving.archive.data import Archive

# External Imports


def _from_archive_o(encoded: dict[str, Any], path: Path) -> Archive:
    """Decodes object dict from archive which is being loaded back up"""

    archive = Archive(path, encoded["url"], encoded["version"])

    # Decode id & body style comment authors
    # NOTE: needed above video decoding for comments
    for kind in encoded["comment_authors"].keys():
        archive.comment_authors[kind] = comment_author.from_archive_ib(
            archive, kind, encoded["comment_authors"][kind]
        )

    # Load up videos/livestreams/shorts
    archive.videos = Videos.from_archive_o(archive, encoded["videos"])
    archive.livestreams = Videos.from_archive_o(archive, encoded["livestreams"])
    archive.shorts = Videos.from_archive_o(archive, encoded["shorts"])

    return archive


def _to_archive_o(archive: Archive) -> dict[str, Any]:
    """Converts all archive data to a object dict to commit"""
    # Encode comment authors
    comment_authors = {}
    for kind in archive.comment_authors.keys():
        comment_authors[kind] = archive.comment_authors[kind]._to_archive_b()

    payload = {
        "version": archive.version,
        "url": archive.url,
        "videos": archive.videos.to_archive_o(),
        "livestreams": archive.livestreams.to_archive_o(),
        "shorts": archive.shorts.to_archive_o(),
        "comment_authors": comment_authors,
    }

    return payload

