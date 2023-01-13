"""Video conversion for formats not supported by the HTML `<video>` tag, our low bar"""

from pathlib import Path
from .errors import _err_msg, ArchiveStructureException, ConversionException
import subprocess
import sys


class Converter:
    def __init__(self, path_videos: Path) -> None:
        _ensure_dir(path_videos)
        self.path_videos = path_videos

    def mkv(self, video_name: str):
        """Converts mkv at path to a fully-supported mp4 video"""
        # Check everything exists
        self._ensure(video_name)

        # Generate/resolve paths
        mkv_path, mp4_path = self._resolve(video_name, ".mp4")

        # Tell ffmpeg to convert
        _ffmpeg_run(["-y", "-i", mkv_path, "-codec", "copy", mp4_path])

    def delete(self):
        """Deletes the current path after conversion"""
        self.path.unlink()

    def _ensure(self, video_name: str):
        """Ensures that everything is ready to go, might error out or raise `FileNotFoundException` exception"""
        _ensure_ffmpeg()
        _ensure_dir(self.path_videos)
        _ensure_file(self._path_video_name(video_name))

    def _resolve(self, video_name: str, new_suffix: str) -> tuple[str, str]:
        """Resolves path and creates a new one with the suffix replaced by the new suffix"""
        path = self._path_video_name(video_name)
        return str(path.resolve()), str(path.with_suffix(new_suffix).resolve())

    def _path_video_name(self, video_name: str) -> Path:
        """Generates path to inputted video name from the baseline converter path"""
        return self.path_videos / video_name


def _ffmpeg_installed() -> bool:
    """Returns if ffmpeg is installed and accessible by running `ffmpeg` as a process like yt-dlp"""
    try:
        _ffmpeg_run(["--help"])
        return True
    except:
        return False


def _ffmpeg_run(args: list[str]):
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


def _ensure_file(path: Path):
    """Ensures that the `path` inputted exists and isn't a dir or raises the `ArchiveStructureException` exception"""
    if not path.exists() or path.is_dir():
        raise ArchiveStructureException(path)


def _ensure_dir(path: Path):
    """Ensures that the `path` inputted exists and isn't a file or raises the `ArchiveStructureException` exception"""
    if not path.exists() or path.is_file():
        raise ArchiveStructureException(path)


def _ensure_ffmpeg():
    """Errors out of the application if ffmpeg is not installed"""
    if not _ffmpeg_installed():
        _err_msg(
            "FFmpeg is needed to convert a video but it wasn't found, please install it!"
        )
        sys.exit(1)