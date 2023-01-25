"""Configuration for metadata/downloads"""

from typing import Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass
import logging

YtDlpSettings = dict[str, Any]
"""Download settings which the `yt-dlp` library uses during initiation"""


@dataclass
class Config:
    max_videos: Optional[int] = None
    max_livestreams: Optional[int] = None
    max_shorts: Optional[int] = None
    skip_download: bool = False
    skip_metadata: bool = False
    comments: bool = False
    format: Optional[str] = None
    proxy: Optional[str] = None
    hook_logger: Any | None = None  # TODO: figure out proper type
    hook_download: Callable[[Any], Any] | None = None  # TODO: figure out proper type

    def submit(self) -> None:
        """Submits configuration, this has the effect of normalising maximums to 0 properly"""
        # Adjust remaining maximums if one is given
        no_maximums = (
            self.max_videos is None
            and self.max_livestreams is None
            and self.max_shorts is None
        )
        if not no_maximums:
            if self.max_videos is None:
                self.max_videos = 0
            if self.max_livestreams is None:
                self.max_livestreams = 0
            if self.max_shorts is None:
                self.max_shorts = 0

        # If all are 0 as its equivalent to skipping download so warn user
        if self.max_videos == 0 and self.max_livestreams == 0 and self.max_shorts == 0:
            logging.warn(
                "Using the skip downloads option is recommended over setting maximums to 0"
            )
            self.skip_download = True

    def settings_dl(self, path: Path) -> YtDlpSettings:
        """Generates customized yt-dlp settings from `config` passed in"""
        settings: YtDlpSettings = {
            # Set the output path
            "outtmpl": f"{path}/videos/%(id)s.%(ext)s",
        }

        # Custom downloading hook
        if self.hook_download is not None:
            settings["progress_hooks"] = [self.hook_download]

        # Custom yt-dlp format
        if self.format is not None:
            settings["format"] = self.format

        # Custom yt-dlp proxy
        if self.proxy is not None:
            settings["proxy"] = self.proxy

        # Return
        return settings

    def settings_md(self) -> YtDlpSettings:
        """Generates customized yt-dlp settings for metadata from `config` passed in"""
        # Always present
        settings: YtDlpSettings = {
            # Skip downloading pending livestreams (#60 <https://github.com/Owez/yark/issues/60>)
            "ignore_no_formats_error": True,
            # Fetch comments from videos
            "getcomments": self.comments,
        }

        # Custom general logger hook
        if self.hook_logger is not None:
            settings["logger"] = self.hook_logger

        # Custom yt-dlp proxy
        if self.proxy is not None:
            settings["proxy"] = self.proxy

        # Return
        return settings
