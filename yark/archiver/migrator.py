"""Migrator for old versions of archives to new ones"""

from pathlib import Path
from colorama import Fore, Style
from .video.element import Element
from ..logger import _err_msg
import sys
from .converter import Converter
from typing import Any, TYPE_CHECKING
from ..utils import ARCHIVE_COMPAT, PYPI_VERSION

if TYPE_CHECKING:
    from .archive import Archive


def _migrate(
    current_version: int,
    expected_version: int,
    encoded: dict,
    path: Path,
    archive_name: str,
) -> dict:
    """Automatically migrates an archive from one version to another by bootstrapping"""

    # Tell user we can't downgrade
    if expected_version < current_version:
        _err_msg(
            f"The version of Yark you're currently using supports up to v{ARCHIVE_COMPAT} archives but your archive is v{current_version}!"
        )
        _err_msg(
            Style.DIM
            + f"To fix this, you might want to upgrade your current Yark {PYPI_VERSION[0]}.{PYPI_VERSION[0]} to a newer one"
            + Style.NORMAL
        )
        sys.exit(1)

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
        # NOTE: this bodged empty archive is fine, its never called on
        for video in encoded["videos"]:
            video["deleted"] = Element.new(Archive(), False)._to_archive_o()
        for video in encoded["livestreams"]:
            video["deleted"] = Element.new(Archive(), False)._to_archive_o()
        for video in encoded["shorts"]:
            video["deleted"] = Element.new(Archive(), False)._to_archive_o()

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
        _err_msg(f"Unknown archive version v{cur} found during migration", True)
        sys.exit(1)

    # Increment version and run again until version has been reached
    cur += 1
    encoded["version"] = cur
    return _step(expected_version, path, cur, encoded, archive_name)


def _o_to_ib_video(
    new_videos: dict[str, dict[str, Any]], video: dict[str, Any]
) -> None:
    """Adds old format `video` into the new `new_videos` dict"""
    id = video["id"]
    del video["id"]
    new_videos[id] = video
