"""Video conversion for formats not supported by the HTML `<video>` tag, our low bar"""

from pathlib import Path
from .errors import _err_msg, FileNotFoundException, ConversionException
import subprocess
import sys


class Converter:
    def __init__(self, path: Path) -> None:
        self.path = path

    def mkv(self):
        """Converts mkv at path to a fully-supported mp4 video"""
        # Check everything exists
        self._ensure()

        # Generate/resolve paths
        mkv_path, mp4_path = self._resolve(".mp4")

        # Tell ffmpeg to convert
        _ffmpeg_run(["-y", "-i", mkv_path, "-codec", "copy", mp4_path])

    def delete(self):
        """Deletes the current path after conversion"""
        self.path.unlink()

    def _ensure(self):
        """Ensures that everything is ready to go, might error out or raise `FileNotFoundException` exception"""
        _ensure_ffmpeg()
        _ensure_file(self.path)

    def _resolve(self, new_suffix: str) -> tuple[Path, Path]:
        """Resolves path and creates a new one with the suffix replaced by the new suffix"""
        return self.path.resolve(), self.path.with_suffix(new_suffix).resolve()


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
    """Ensures that the `path` inputted exists and isn't a dir or raises the `FileNotFoundException` exception"""
    if not path.exists() or path.is_dir():
        raise FileNotFoundException(path)


def _ensure_ffmpeg():
    """Errors out of the application if ffmpeg is not installed"""
    if not _ffmpeg_installed():
        _err_msg(
            "FFmpeg is needed to convert a video but it wasn't found, please install it!"
        )
        sys.exit(1)
