"""Video conversion for formats not supported by the HTML `<video>` tag, our low bar"""
# Standard Imports
import sys
from pathlib import Path
import subprocess

# Local Imports
from yark.yark.exceptions import ArchiveStructureException, ConversionException
from yark.yark.utils import log_err

# External Imports


class Converter:
    path_videos: Path

    def __init__(self, path_videos: Path) -> None:
        self.path_videos = path_videos

    def run(self) -> None:
        """Goes through the videos directory given and converts all videos we can, e.g. mkv to mp4"""
        # Convert mkv videos
        for path in self.path_videos.glob("*.mkv"):
            self._convert_copy_codec(path)

        # Convert 3gp videos
        for path in self.path_videos.glob("*.3gp"):
            self._convert_copy_codec(path)

    def _convert_copy_codec(self, path: Path) -> None:
        """Runs complete conversion process for ffmpeg commands which can copy codecs"""
        # Check everything exists
        self._ensure(path)

        # Generate/resolve paths
        mkv_path, mp4_path = self._resolve(path, ".mp4")

        # Tell ffmpeg to convert
        _ffmpeg_run(["-y", "-i", mkv_path, "-codec", "copy", mp4_path])

        # Delete the original path
        path.unlink()

    def _ensure(self, path: Path) -> None:
        """Ensures that everything is ready to go, might error out or raise `FileNotFoundException` exception"""
        _ensure_ffmpeg()
        _ensure_dir(self.path_videos)
        _ensure_file(path)

    def _resolve(self, path: Path, new_suffix: str) -> tuple[str, str]:
        """Resolves path and creates a new one with the suffix replaced by the new suffix"""
        return str(path.resolve()), str(path.with_suffix(new_suffix).resolve())


def _ffmpeg_installed() -> bool:
    """Returns if ffmpeg is installed and accessible by running `ffmpeg` as a process like yt-dlp"""
    try:
        _ffmpeg_run(["--help"])
        return True
    except:
        return False


def _ffmpeg_run(args: list[str]) -> None:
    """Runs an ffmpeg command with the `args` provided, raises `ConversionException` exception if command failed"""
    # Add ffmpeg to start of args
    process_args = ["ffmpeg"]
    process_args.extend(args)

    # Run the process for ffmpeg
    process = subprocess.Popen(
        process_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Poll for return code meaning it's finished
    while True:
        # Poll for the status code (if any)
        poll = process.poll()

        # Command finished
        if poll is not None:
            # Error whilst running
            if poll == 1:
                stderr = (
                    process.stderr.read().decode()
                    if process.stderr is not None
                    else "Unknown error"
                )
                raise ConversionException(stderr)

            # Command completed successfully
            break


def _ensure_file(path: Path) -> None:
    """Ensures that the `path` inputted exists and isn't a dir or raises the `ArchiveStructureException` exception"""
    if not path.exists() or path.is_dir():
        raise ArchiveStructureException(path)


def _ensure_dir(path: Path) -> None:
    """Ensures that the `path` inputted exists and isn't a file or raises the `ArchiveStructureException` exception"""
    if not path.exists() or path.is_file():
        raise ArchiveStructureException(path)


def _ensure_ffmpeg() -> None:
    """Errors out of the application if ffmpeg is not installed"""
    if not _ffmpeg_installed():
        log_err(
            "FFmpeg is needed to convert a video but it wasn't found, please install it!"
        )
        sys.exit(1)
