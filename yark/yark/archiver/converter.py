"""Video conversion for formats not supported by the HTML `<video>` tag, our low bar"""

from pathlib import Path
from ..errors import ArchiveStructureException, ConversionException
from ..utils import _log_err
import subprocess
import sys


class Converter:
    """
    FFMPEG-based converter which transfers all video formats from YouTube into a standardized MP4 format
    
    The reasoning behind this is to:

    1. Simplify the distribution of videos, and so you can rigidly assume an id of `x` would be at `videos/x.mp4`
    2. There's no massive drawbacks as most formats can have their container copied straight into MP4s
    3. The reason MP4s where picked over WEBMs is because of compat, see https://github.com/tauri-apps/tauri/issues/5605

    There's pros and cons to this and originally we assumed it was either MP4 or WEBM, but having a single format to rule them all works out well
    """

    path_videos: Path

    def __init__(self, path_videos: Path) -> None:
        self.path_videos = path_videos

    def run(self) -> None:
        """Goes through the videos directory given and converts all videos we can to mp4, e.g. mkv to mp4"""
        # Convert mkv videos
        for path in self.path_videos.glob("*.mkv"):
            self._convert_copy_codec(path)

        # Convert 3gp videos
        for path in self.path_videos.glob("*.3gp"):
            self._convert_copy_codec(path)

        # Convert webm videos, the most common kind
        # NOTE: ideally we'd allow mp4 and webm but the tauri viewer dislikes webm on macos, see <https://github.com/tauri-apps/tauri/issues/5605>
        for path in self.path_videos.glob("*.webm"):
            self._convert_copy_codec(path)

    def _convert_copy_codec(self, path: Path) -> None:
        """Runs complete conversion process for ffmpeg commands which can copy codecs"""
        # Check everything exists
        self._ensure(path)

        # Generate/resolve paths
        in_path, mp4_path = self._resolve(path, ".mp4")

        # Tell ffmpeg to convert
        _ffmpeg_run(["-y", "-i", in_path, "-codec", "copy", mp4_path])

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
        _log_err(
            "FFmpeg is needed to convert a video but it wasn't found, please install it!"
        )
        sys.exit(1)
