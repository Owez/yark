from typing import Any
from yark.archiver.config import DownloadLogger


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


