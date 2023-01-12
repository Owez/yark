from typing import Optional
from colorama import Fore


class Config:
    max_videos: Optional[int]
    max_livestreams: Optional[int]
    max_shorts: Optional[int]
    skip_download: bool
    skip_metadata: bool
    comments: bool
    format: Optional[str]

    def __init__(self) -> None:
        self.max_videos = None
        self.max_livestreams = None
        self.max_shorts = None
        self.skip_download = False
        self.skip_metadata = False
        self.comments = False
        self.format = None

    def submit(self):
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
