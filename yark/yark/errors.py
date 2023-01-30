"""Exceptions and error functions"""

from pathlib import Path


class ArchiveNotFoundException(Exception):
    """Archive couldn't be found, the name was probably incorrect"""

    def __init__(self, path: Path, *args: object) -> None:
        super().__init__(*args)
        self.path = path


class MetadataFailException(Exception):
    """Could not download or parse metadata for an archive"""


class VideoNotFoundException(Exception):
    """Video couldn't be found, the id was probably incorrect"""


class NoteNotFoundException(Exception):
    """Note couldn't be found, the id was probably incorrect"""


class TimestampException(Exception):
    """Invalid timestamp inputted for note"""


class ArchiveStructureException(Exception):
    """Directory or file inside of an archive for a required operation couldn't be found when it should've"""

    def __init__(self, path: Path, *args: object) -> None:
        super().__init__(*args)
        self.path = path


class ConversionException(Exception):
    """Couldn't convert a video file format to a different one because of an error with FFmpeg"""

    def __init__(
        self,
        stderr: str,
        *args: object,
    ) -> None:
        super().__init__(*args)
        self.stderr = stderr
