"""Migrator for old versions of archives to new ones"""
# Standard Imports
import sys
from typing import Any
from pathlib import Path
import datetime
import logging

# Local Imports
from yark.archiving.archiver import Converter
from yark.yark.utils import ARCHIVE_SCHEMA_COMPAT, PYPI_VERSION, log_err

# External Imports
from colorama import Style


def migrate(
    current_version: int,
    expected_version: int,
    encoded: dict[str, Any],
    path: Path,
    archive_name: str,
) -> dict[str, Any]:
    """Automatically migrates an archive from one version to another by bootstrapping"""

    # Tell user we can't downgrade
    if expected_version < current_version:
        log_err(
            f"The version of Yark you're currently using supports up to v{ARCHIVE_SCHEMA_COMPAT} "
            f"archives but your archive is v{current_version}!"
        )
        log_err(
            f'{Style.DIM}'
            f"To fix this, you might want to upgrade your current "
            f"Yark {PYPI_VERSION[0]}.{PYPI_VERSION[0]} to a newer one"
            f'{Style.NORMAL}'
        )

    # Inform user of the backup process
    logging.warning(
        f"Automatically migrating archive from v{current_version} to v{expected_version}, "
        f"a backup has been made at {archive_name}/yark.bak"
    )

    return step(expected_version, path, current_version, encoded, archive_name)


def step(
    expected_version: int,
    path: Path,
    cur: int,
    encoded: dict[str, Any],
    archive_name: str,
) -> dict[str, Any]:
    """Step in recursion to migrate from one to another, contains migration logic"""
    # Stop because we've reached the desired version
    if cur == expected_version:
        return encoded

    # From version 1 to version 2
    elif cur == 1:
        # Target id to url
        encoded["url"] = "https://www.youtube.com/channel/" + encoded["id"]
        del encoded["id"]
        logging.warn("Please make sure " + encoded["url"] + " is the correct url")

        # Empty livestreams/shorts lists
        encoded["livestreams"] = []
        encoded["shorts"] = []

    # From version 2 to version 3
    elif cur == 2:
        # Add deleted status to every video/livestream/short
        not_deleted = {datetime.datetime.utcnow().isoformat(): False}
        for video in encoded["videos"]:
            video["deleted"] = not_deleted
        for video in encoded["livestreams"]:
            video["deleted"] = not_deleted
        for video in encoded["shorts"]:
            video["deleted"] = not_deleted

    # From version 3 to version 4
    elif cur == 3:
        # Add empty comment author store
        encoded["comment_authors"] = {}

        # Add blank comment section to each video
        for video in encoded["videos"]:
            video["comments"] = {}
        for video in encoded["livestreams"]:
            video["comments"] = {}
        for video in encoded["shorts"]:
            video["comments"] = {}

        # Rename thumbnails directory to images
        try:
            thumbnails = path / "thumbnails"
            thumbnails.rename(path / "images")
        except:
            log_err(
                f"Couldn't rename {archive_name}/thumbnails directory to {archive_name}/images, please manually rename to continue!"
            )
            sys.exit(1)

        # Make each video category use "id": {"body"} instead of {"id", "body"}
        new_videos: dict[str, dict[str, Any]] = {}
        for video in encoded["videos"]:
            _o_to_ib_video(new_videos, video)
        encoded["videos"] = new_videos

        new_livestreams: dict[str, dict[str, Any]] = {}
        for video in encoded["livestreams"]:
            _o_to_ib_video(new_livestreams, video)
        encoded["livestreams"] = new_livestreams

        new_shorts: dict[str, dict[str, Any]] = {}
        for video in encoded["shorts"]:
            _o_to_ib_video(new_shorts, video)
        encoded["shorts"] = new_shorts

        # Convert unsupported formats, because of #75 <https://github.com/Owez/yark/issues/75>
        converter = Converter(path / "videos")
        converter.run()

    # Unknown version
    else:
        log_err(f"Unknown archive version v{cur} found during migration", True)
        sys.exit(1)

    # Increment version and run again until version has been reached
    cur += 1
    encoded["version"] = cur
    return step(expected_version, path, cur, encoded, archive_name)


def _o_to_ib_video(
    new_videos: dict[str, dict[str, Any]], video: dict[str, Any]
) -> None:
    """Adds old format `video` into the new `new_videos` dict"""
    kind = video["id"]
    del video["id"]
    new_videos[kind] = video
