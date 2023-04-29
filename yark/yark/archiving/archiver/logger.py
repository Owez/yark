# Standard Imports
from typing import Any

# Local Imports

# External Imports


class DownloadLogger:
    """Quiet logger extension for removing any stdout from yt-dlp components"""

    @staticmethod
    def downloading(d: dict[str, Any]) -> None:
        """Progress hook for video downloading, ignored"""
        pass

    def debug(self, msg: str) -> None:
        """Debug log messages, ignored"""
        pass

    def info(self, msg: str) -> None:
        """Info log messages, ignored"""
        pass

    def warning(self, msg: str) -> None:
        """Warning log messages, ignored"""
        pass

    def error(self, msg: str) -> None:
        """Error log messages, ignored"""
        pass


class DownloadProgressLogger(DownloadLogger):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def downloading(d: dict[str, Any]) -> None:
        """Progress hook for video downloading, ignored"""
        if "_percent_str" in d:
            global download_progress_percentage
            download_progress_percentage = float(d["_percent_str"][:-1])


download_progress_percentage: float = 0.0
"""Percentage of the current video being downloaded from `DownloadProgressLogger` for use in progress reporting"""


