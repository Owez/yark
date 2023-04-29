# Standard Imports
import logging
from pathlib import Path

# Local Imports
from yark.yark.archiving.archive.data.archive import RawMetadata
from yark.yark.archiving.config.data import Config
from yark.yark.exceptions import MetadataFailException
from yark.yark.archiving.archiver import download

# External Imports
from yt_dlp import YoutubeDL


class ArchiveManager:

    def __init__(self, path: Path, url: str):
        self.path = path
        self.url = url

        self.archive = None
        self.videos_path = Path(f'{self.path}/videos/')

    def _clean_parts(self) -> None:
        """Cleans old temporary `.part` files which where stopped during download if present"""
        # Make a bucket for found files
        deletion_bucket: list[Path] = []

        # Scan through and find part files
        videos = self.path / "videos"
        deletion_bucket.extend([file for file in videos.glob("*.part")])
        deletion_bucket.extend([file for file in videos.glob("*.ytdl")])

        # Log and delete if there are part files present
        if len(deletion_bucket) != 0:
            logging.info("Cleaning out previous temporary files..")
            for file in deletion_bucket:
                file.unlink()

