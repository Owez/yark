"""Migrator for old versions of archives to new ones"""

from pathlib import Path
from colorama import Fore, Style
from .video import Video, Element
from ..logger import _err_msg
import sys
from .converter import Converter


def _migrate(
    current_version: int,
    expected_version: int,
    encoded: dict,
    path: Path,
    archive_name: str,
) -> dict:
    """Automatically migrates an archive from one version to another by bootstrapping"""

    # Inform user of the backup process
    print(
        Fore.YELLOW
        + f"Automatically migrating archive from v{current_version} to v{expected_version}, a backup has been made at {archive_name}/yark.bak"
        + Fore.RESET
    )

    # Start recursion step
    return _step(expected_version, path, current_version, encoded, archive_name)


def _step(
    expected_version: int, path: Path, cur: int, encoded: dict, archive_name: str
) -> dict:
    """Step in recursion to migrate from one to another, contains migration logic"""
    # Stop because we've reached the desired version
    if cur == expected_version:
        return encoded

    # From version 1 to version 2
    elif cur == 1:
        # Target id to url
        encoded["url"] = "https://www.youtube.com/channel/" + encoded["id"]
        del encoded["id"]
        print(
            Fore.YELLOW
            + "Please make sure "
            + encoded["url"]
            + " is the correct url"
            + Fore.RESET
        )

        # Empty livestreams/shorts lists
        encoded["livestreams"] = []
        encoded["shorts"] = []

    # From version 2 to version 3
    elif cur == 2:
        # Add deleted status to every video/livestream/short
        # NOTE: none is fine for new elements, just a slight bodge
        for video in encoded["videos"]:
            video["deleted"] = Element.new(Video._new_empty(), False)._to_archive_o()
        for video in encoded["livestreams"]:
            video["deleted"] = Element.new(Video._new_empty(), False)._to_archive_o()
        for video in encoded["shorts"]:
            video["deleted"] = Element.new(Video._new_empty(), False)._to_archive_o()

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
            _err_msg(
                f"Couldn't rename {archive_name}/thumbnails directory to {archive_name}/images, please manually rename to continue!"
            )
            sys.exit(1)

        # Convert unsupported formats, because of #75 <https://github.com/Owez/yark/issues/75>
        converter = Converter(path / "videos")
        converter.run()

    # Unknown version
    else:
        _err_msg(f"Unknown archive version v{cur} found during migration", True)
        sys.exit(1)

    # Increment version and run again until version has been reached
    cur += 1
    encoded["version"] = cur
    return _step(expected_version, path, cur, encoded, archive_name)
