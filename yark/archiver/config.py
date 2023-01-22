"""Configuration for metadata/downloads"""

from typing import Optional, Any
from colorama import Fore
from ..logger import VideoLogger
from pathlib import Path
from dataclasses import dataclass

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

        # If all are 0 as its equivalent to skipping download
        if self.max_videos == 0 and self.max_livestreams == 0 and self.max_shorts == 0:
            print(
                Fore.YELLOW
                + "Using the skip downloads option is recommended over setting maximums to 0"
                + Fore.RESET
            )
            self.skip_download = True

    def settings_dl(self, path: Path) -> YtDlpSettings:
        """Generates customized yt-dlp settings from `config` passed in"""
        settings = {
            # Set the output path
            "outtmpl": f"{path}/videos/%(id)s.%(ext)s",
            # Centralized logger hook for ignoring all stdout
            "logger": VideoLogger(),
            # Logger hook for download progress
            "progress_hooks": [VideoLogger.downloading],
        }

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
        settings = {
            # Centralized logging system; makes output fully quiet
            "logger": VideoLogger(),
            # Skip downloading pending livestreams (#60 <https://github.com/Owez/yark/issues/60>)
            "ignore_no_formats_error": True,
            # Fetch comments from videos
            "getcomments": self.comments,
        }

        # Custom yt-dlp proxy
        if self.proxy is not None:
            settings["proxy"] = self.proxy

        # Return
        return settings
