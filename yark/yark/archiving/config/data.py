"""Configuration for metadata/downloads"""
# Standard Imports
from typing import Any
from dataclasses import dataclass
from pathlib import Path
import logging

# Local Imports

# External Imports


YtDlpSettings = dict[str, Any]
"""Download settings which the `yt-dlp` library uses during initiation"""


@dataclass
class Config:
    max_videos: int | None = None
    max_livestreams: int | None = None
    max_shorts: int | None = None
    skip_download: bool = False
    skip_metadata: bool = False
    comments: bool = False
    format: str | None = None
    proxy: str | None = None

    def submit(self) -> None:
        """Submits configuration, this has the effect of normalising maximums to 0 properly"""
        # Adjust remaining maximums if one is given
        no_maximums = (
            self.max_videos is None
            and self.max_livestreams is None
            and self.max_shorts is None
        )
        if not no_maximums:
            self.max_videos = 0 if self.max_videos is None else self.max_videos
            self.max_livestreams = 0 if self.max_livestreams is None else self.max_livestreams
            self.max_shorts = 0 if self.max_shorts is None else self.max_shorts

        # If all are 0 as its equivalent to skipping download so warn user
        if self.max_videos == 0 and self.max_livestreams == 0 and self.max_shorts == 0:
            logging.warning(
                "Using the skip downloads option is recommended over setting maximums to 0"
            )
            self.skip_download = True

    def settings_dl(self, path: Path) -> YtDlpSettings:
        """Generates customized yt-dlp settings from `config` passed in"""
        settings: YtDlpSettings = {
            "outtmpl": f"{path}/videos/%(id)s.%(ext)s",
            "logger": self.hook_logger(),
            "progress_hooks": [self.hook_logger.downloading],
        }

        # Custom yt-dlp format
        if self.format is not None:
            settings["format"] = self.format

        # Custom yt-dlp proxy
        if self.proxy is not None:
            settings["proxy"] = self.proxy

        return settings

    def into_metadata_settings(self) -> YtDlpSettings:
        """Generates customized yt-dlp settings for metadata from `config` passed in"""
        # Always present
        settings: YtDlpSettings = {
            # Skip downloading pending livestreams (#60 <https://github.com/Owez/yark/issues/60>)
            "ignore_no_formats_error": True,
            # Fetch comments from videos
            "getcomments": self.comments,
        }

        # Custom yt-dlp proxy
        if self.proxy is not None:
            settings["proxy"] = self.proxy

        return settings

