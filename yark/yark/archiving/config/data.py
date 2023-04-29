"""Configuration for metadata/downloads"""
# Standard Imports
from typing import Any

import os
from typing import Optional, Any, Callable, Type
from pathlib import Path
from dataclasses import dataclass
from pathlib import Path
import logging
import webbrowser

# Local Imports

# External Imports


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
    format: str | None = None
    proxy: str | None = None
    cookies: Optional[str] = None
    bind_host: Optional[str] = None
    bind_port: int = 7667
    headless: bool = False
    hook_logger: Type[DownloadLogger] = DownloadLogger
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
            logging.warning(
                "Using the skip downloads option is recommended over setting maximums to 0"
            )
            self.skip_download = True

        # If running under docker, override some logical values
        if os.environ.get("DOCKER_CONTAINER") == "1":
            self.bind_host = "0.0.0.0"
            self.headless = True

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

        # Cookies file to allow, for example, archiving private playlists
        if self.cookies is not None:
            settings["cookiefile"] = self.cookies

        # Return
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

        # Cookies file to allow, for example, archiving private playlists
        if self.cookies is not None:
            settings["cookiefile"] = self.cookies

        # Return
        return settings

    def browser_url(self, archive_name: Optional[str]) -> str:
        """Returns the URL to be passed to the browser based on the host/port from the configuration"""
        # Default URL returns 127.0.0.1 as the host
        bind_host = "127.0.0.1"

        # If the bind_host config is set then change it from "127.0.0.1"
        if self.bind_host is not None:
            bind_host = self.bind_host

        # If the archive_name is not set, then add it to the URL
        if archive_name is not None:
            return f"http://{bind_host}:{self.bind_port}/archive/{archive_name}/videos"

        return f"http://{bind_host}:{self.bind_port}/"

    def open_webbrowser(self, archive_name: Optional[str]):
        """Opens the webbrowser to optional archive_name or to the main page if not specified"""
        url = self.browser_url(archive_name)

        webbrowser.open(url)

