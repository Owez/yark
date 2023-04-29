"""Exceptions and error functions"""
# Standard Imports
from pathlib import Path

# Local Imports

# External Imports


class ArchiveNotFoundException(Exception):

    def __init__(self, path: Path, *args) -> None:
        super().__init__(*args)
        self.path = path

    def __str__(self):
        raise NotImplementedError


class ConfigNotFoundException(Exception):

    def __init__(self, path: Path, *args):
        super().__init__(*args)
        self.path = path

    def __str__(self):
        return f"Could not find archiving configuration at '{self.path}'"


class MetadataFailException(Exception):
    """Could not download or parse metadata for an archive"""


class VideoNotFoundException(Exception):
    """Video couldn't be found, the id was probably incorrect"""


class NoteNotFoundException(Exception):
    """Note couldn't be found, the id was probably incorrect"""


class TimestampException(Exception):
    """Invalid timestamp inputted for note"""


class ArchiveStructureException(Exception):
    """Directory or file inside an archive for a required operation couldn't be found when it should've"""

    def __init__(self, path: Path, *args: object) -> None:
        super().__init__(*args)
        self.path = path


class ConversionException(Exception):
    """Couldn't convert a video file format to a different one because of an error with FFmpeg"""

    def __init__(self, stderr: str, *args: object) -> None:
        super().__init__(*args)
        self.stderr = stderr
