"""Channel and overall archive management with downloader."""

from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from yt_dlp import DownloadError, YoutubeDL  # type: ignore

from ..errors import ArchiveNotFoundException, VideoNotFoundException
from ..terminal import ui
from .reporter import Reporter
from .video import Element, Video

ARCHIVE_COMPAT = 3
"""
Version of Yark archives which this script is capable of properly parsing

- Version 1 was the initial format and had all the basic information you can see in the viewer now
- Version 2 introduced livestreams and shorts into the mix, as well as making the channel id into a simple url
- Version 3 was a minor change to introduce a deleted tag so we have full reporting capability

Some of these breaking versions are large changes and some are relatively small.
We don't check if a value exists or not in the archive format out of precedent
and we don't have optionally-present values, meaning that any new tags are a
breaking change to the format. The only downside to this is that the migrator
gets a line or two of extra code every breaking change. This is much better than
having way more complexity in the archiver decoding system itself.
"""


class DownloadConfig:
    videos: "DownloadSelection"
    livestreams: "DownloadSelection"
    shorts: "DownloadSelection"
    uploaded_after: Optional[datetime]
    uploaded_before: Optional[datetime]
    verbose: bool
    respect_rate_limits: bool
    skip_download: bool
    skip_metadata: bool
    format: Optional[str]

    def __init__(self) -> None:
        self.videos = DownloadSelection()
        self.livestreams = DownloadSelection()
        self.shorts = DownloadSelection()
        self.uploaded_after = None
        self.uploaded_before = None
        self.verbose = False
        self.respect_rate_limits = False
        self.skip_download = False
        self.skip_metadata = False
        self.format = None

    def submit(self):
        """Submits configuration, this has the effect of normalising maximums to 0 properly"""
        if (
            self.uploaded_after is not None
            and self.uploaded_before is not None
            and self.uploaded_after > self.uploaded_before
        ):
            raise ValueError("The minimum upload date cannot be after the maximum")

        # Adjust remaining maximums if one is given
        no_maximums = (
            self.videos.maximum is None
            and self.livestreams.maximum is None
            and self.shorts.maximum is None
        )
        if not no_maximums:
            if self.videos.maximum is None:
                self.videos.maximum = 0
            if self.livestreams.maximum is None:
                self.livestreams.maximum = 0
            if self.shorts.maximum is None:
                self.shorts.maximum = 0

        # If all are 0 as its equivalent to skipping download
        if (
            self.videos.maximum == 0
            and self.livestreams.maximum == 0
            and self.shorts.maximum == 0
        ):
            ui.warning(
                "Using the skip downloads option is recommended over setting maximums to 0"
            )
            self.skip_download = True


class DownloadFilter(str, Enum):
    """Supported download selection strategies."""

    RECENT = "recent"
    POPULAR = "popular"


@dataclass
class DownloadSelection:
    """Selection rule for one media category."""

    maximum: Optional[int] = None
    filter: DownloadFilter = DownloadFilter.RECENT


class VideoLogger:
    def __init__(
        self,
        verbose: bool = False,
        show_progress: bool = False,
        progress_label: str = "Progress",
    ) -> None:
        self.verbose = verbose
        self.show_progress = show_progress
        self.progress_label = progress_label
        self._last_progress: tuple[int, int] | None = None

    def _emit_progress(self, msg: str) -> None:
        if not self.show_progress:
            return

        match = re.search(r"Downloading item (\d+) of (\d+)", msg)
        if match is None:
            return

        current = int(match.group(1))
        total = int(match.group(2))
        step = max(total // 20, 1)

        should_emit = (
            self._last_progress is None
            or self._last_progress[1] != total
            or current == 1
            or current == total
            or current - self._last_progress[0] >= step
        )
        if should_emit:
            ui.info(f"{self.progress_label}: {current}/{total}")
            self._last_progress = (current, total)

    @staticmethod
    def downloading(d):
        """Progress hook for video downloading"""
        # Get video's id
        id = d["info_dict"]["id"]

        # Finished a video's download
        if d["status"] == "finished":
            ui.success(f"Downloaded {id}")

    def debug(self, msg):
        """Debug log messages"""
        self._emit_progress(msg)
        if self.verbose:
            ui.plain(f"[yt-dlp:debug] {msg}")

    def info(self, msg):
        """Info log messages"""
        self._emit_progress(msg)

        if self.verbose:
            ui.plain(f"[yt-dlp:info] {msg}")

    def warning(self, msg):
        """Warning log messages"""
        if self.verbose:
            ui.warning(f"[yt-dlp:warn] {msg}")

    def error(self, msg):
        """Error log messages"""
        if self.verbose:
            ui.error(f"[yt-dlp:error] {msg}")


class Channel:
    path: Path
    version: int
    url: str
    videos: list[Video]
    livestreams: list[Video]
    shorts: list[Video]
    reporter: Reporter
    cookies_file: Optional[Path]
    verbose: bool

    @staticmethod
    def new(path: Path, url: str) -> Channel:
        """Creates a new channel"""
        # Details
        ui.info("Creating new channel..")
        channel = Channel()
        channel.path = Path(path)
        channel.version = ARCHIVE_COMPAT
        channel.url = url
        channel.videos = []
        channel.livestreams = []
        channel.shorts = []
        channel.cookies_file = None
        channel.verbose = False
        channel.reporter = Reporter(channel)

        # Commit and return
        channel.commit()
        return channel

    @staticmethod
    def _new_empty() -> Channel:
        """Lightweight dummy for migration, never touches the filesystem."""
        channel = Channel()
        channel.path = Path(".")
        channel.version = ARCHIVE_COMPAT
        channel.url = ""
        channel.videos = []
        channel.livestreams = []
        channel.shorts = []
        channel.cookies_file = None
        channel.verbose = False
        channel.reporter = Reporter(channel)
        return channel

    @staticmethod
    def load(path: Path) -> Channel:
        """Loads existing channel from path"""
        # Check existence
        path = Path(path)
        channel_name = path.name
        ui.info(f"Loading {channel_name} channel..")
        if not path.exists():
            raise ArchiveNotFoundException("Archive doesn't exist")

        # Load config
        encoded = json.load(open(path / "yark.json", "r"))

        # Check version before fully decoding and exit if wrong
        archive_version = encoded["version"]
        if archive_version != ARCHIVE_COMPAT:
            encoded = _migrate_archive(
                archive_version, ARCHIVE_COMPAT, encoded, channel_name
            )

        # Decode and return
        return Channel._from_dict(encoded, path)

    def metadata(self, config: Optional[DownloadConfig] = None):
        """Queries YouTube for all channel metadata to refresh known videos"""
        self._verbose(f"Starting metadata fetch for {self.url}")
        with ui.status("Downloading metadata.."):
            res = self._download_metadata(config)
        self._verbose(
            f"Metadata root keys: {', '.join(sorted(res.keys()))}; top-level entries: {len(res.get('entries', []))}"
        )

        # Uncomment for saving big dumps for testing
        # with open(self.path / "dump.json", "w+") as file:
        #     json.dump(res, file)

        # Uncomment for loading big dumps for testing
        # res = json.load(open(self.path / "dump.json", "r"))

        # Parse downloaded metadata
        self._parse_metadata(res)

    def _download_metadata(self, config: Optional[DownloadConfig]) -> dict[str, Any]:
        """Downloads metadata dict and returns for further parsing"""
        # Construct downloader
        settings = {
            # Centralized logging system; makes output fully quiet
            "logger": VideoLogger(
                verbose=self.verbose,
                show_progress=not self.verbose,
                progress_label="Metadata progress",
            ),
            # Skip downloading pending livestreams (#60 <https://github.com/Owez/yark/issues/60>)
            "ignore_no_formats_error": True,
            # Concurrent fragment downloading for increased resilience (#109 <https://github.com/Owez/yark/issues/109>)
            "concurrent_fragment_downloads": 8,
            # Keep yt-dlp progress lines available for parsing in normal mode,
            # while full details are still only printed when self.verbose is enabled.
            "verbose": True,
        }
        if config is not None and config.respect_rate_limits:
            settings.update(
                {
                    "sleep_interval_requests": 1,
                    "sleep_interval": 1,
                    "max_sleep_interval": 5,
                    "retries": 10,
                    "extractor_retries": 10,
                    "socket_timeout": 30,
                }
            )
            self._verbose("Rate-limit compliance mode enabled for metadata")
        self._apply_cookie_settings(settings)

        # Get response and snip it
        with YoutubeDL(settings) as ydl:
            for i in range(3):
                try:
                    res: dict[str, Any] = ydl.extract_info(self.url, download=False)
                    return res
                except Exception as exception:
                    # Report error
                    retrying = i != 2
                    _err_dl("metadata", exception, retrying)

                    # Print retrying message
                    if retrying:
                        ui.warning("Retrying metadata download..")

    def _parse_metadata(self, res: dict[str, Any]):
        """Parses entirety of downloaded metadata"""
        # Normalize into types of videos
        videos = []
        livestreams = []
        shorts = []
        if len(res["entries"]) > 0 and "entries" not in res["entries"][0]:
            # Videos only
            videos = res["entries"]
            self._verbose(
                f"Detected single bucket metadata; treating all {len(videos)} entries as videos"
            )
        else:
            # Videos and at least one other (livestream/shorts)
            for entry in res["entries"]:
                kind = entry["title"].split(" - ")[-1].lower()
                if kind == "videos":
                    videos = entry["entries"]
                elif kind == "live":
                    livestreams = entry["entries"]
                elif kind == "shorts":
                    shorts = entry["entries"]
                else:
                    ui.error(f"Unknown video kind '{kind}' found", True)
            self._verbose(
                "Detected bucketed metadata; "
                f"videos={len(videos)}, livestreams={len(livestreams)}, shorts={len(shorts)}"
            )

        # Parse metadata
        self._parse_metadata_videos("video", videos, self.videos)
        self._parse_metadata_videos("livestream", livestreams, self.livestreams)
        self._parse_metadata_videos("shorts", shorts, self.shorts)

        # Go through each and report deleted
        self._report_deleted(self.videos)
        self._report_deleted(self.livestreams)
        self._report_deleted(self.shorts)

    def download(self, config: DownloadConfig):
        """Downloads all videos which haven't already been downloaded"""
        self._verbose("Starting download phase")
        # Clean out old part files
        self._clean_parts()

        # Create settings for the downloader
        settings = {
            # Set the output path
            "outtmpl": f"{self.path}/videos/%(id)s.%(ext)s",
            # Centralized logger hook for ignoring all stdout
            "logger": VideoLogger(self.verbose),
            # Logger hook for download progress
            "progress_hooks": [VideoLogger.downloading],
            # Let yt-dlp emit more details when requested by user.
            "verbose": self.verbose,
        }
        if config.respect_rate_limits:
            settings.update(
                {
                    "sleep_interval_requests": 1,
                    "sleep_interval": 1,
                    "max_sleep_interval": 5,
                    "retries": 10,
                    "extractor_retries": 10,
                    "socket_timeout": 30,
                }
            )
            self._verbose("Rate-limit compliance mode enabled for download")
        self._apply_cookie_settings(settings)
        if config.format is not None:
            settings["format"] = config.format

        # Attach to the downloader
        with YoutubeDL(settings) as ydl:
            # Retry downloading 5 times in total for all videos
            for i in range(5):
                # Try to curate a list and download videos on it
                try:
                    # Curate list of non-downloaded videos
                    not_downloaded = self._curate(config)
                    self._verbose(f"Curated {len(not_downloaded)} videos for download")

                    # Stop if there's nothing to download
                    if len(not_downloaded) == 0:
                        break

                    # Print curated if this is the first time
                    if i == 0:
                        fmt_num = (
                            "a new video"
                            if len(not_downloaded) == 1
                            else f"{len(not_downloaded)} new videos"
                        )
                        ui.info(f"Downloading {fmt_num}..")

                    # Continuously try to download after private/deleted videos are found
                    # This block gives the downloader all the curated videos and skips/reports deleted videos by filtering their exceptions
                    while True:
                        # Download from curated list then exit the optimistic loop
                        try:
                            urls = [video.url() for video in not_downloaded]
                            if self.verbose and len(urls) > 0:
                                preview = ", ".join(video.id for video in not_downloaded[:5])
                                suffix = "..." if len(not_downloaded) > 5 else ""
                                self._verbose(
                                    f"Downloading IDs: {preview}{suffix}"
                                )
                            ydl.download(urls)
                            break

                        # Special handling for private/deleted videos which are archived, if not we raise again
                        except DownloadError as exception:
                            # Video is privated or deleted
                            if (
                                "Private video" in exception.msg
                                or "This video has been removed by the uploader"
                                in exception.msg
                            ):
                                # Skip video from curated and get it as a return
                                not_downloaded, video = _skip_video(
                                    not_downloaded, "deleted"
                                )

                                # If this is a new occurrence then set it & report
                                # This will only happen if its deleted after getting metadata, like in a dry run
                                if video.deleted.current() == False:
                                    self.reporter.deleted.append(video)
                                    video.deleted.update(None, True)

                            # User hasn't got ffmpeg installed and youtube hasn't got format 22
                            # NOTE: see #55 <https://github.com/Owez/yark/issues/55> to learn more
                            # NOTE: sadly yt-dlp doesn't let us access yt_dlp.utils.ContentTooShortError so we check msg
                            elif " bytes, expected " in exception.msg:
                                # Skip video from curated
                                not_downloaded, _ = _skip_video(
                                    not_downloaded,
                                    "no format found; please download ffmpeg!",
                                    True,
                                )

                            # Nevermind, normal exception
                            else:
                                raise exception

                    # Stop if we've got them all
                    break

                # Report error and retry/stop
                except Exception as exception:
                    # Report error
                    _err_dl("videos", exception, i != 4)

    def search(self, id: str):
        """Searches channel for a video with the corresponding `id` and returns"""
        # Search
        for video in self.videos:
            if video.id == id:
                return video

        # Raise exception if it's not found
        raise VideoNotFoundException(f"Couldn't find {id} inside archive")

    def _curate(self, config: DownloadConfig) -> list[Video]:
        """Curate videos which aren't downloaded and return their urls"""

        def curate_list(
            videos: list[Video], selection: DownloadSelection
        ) -> list[Video]:
            """Curates the videos inside of the provided bucket using the provided selection rule."""
            available = [video for video in videos if not video.downloaded()]
            if config.uploaded_after is not None:
                available = [
                    video for video in available if video.uploaded >= config.uploaded_after
                ]
            if config.uploaded_before is not None:
                available = [
                    video for video in available if video.uploaded <= config.uploaded_before
                ]

            if selection.filter == DownloadFilter.POPULAR:
                available.sort(
                    key=lambda video: (
                        video.views.current() if video.views.current() is not None else -1,
                        video.uploaded,
                    ),
                    reverse=True,
                )
            else:
                available.sort(key=lambda video: video.uploaded, reverse=True)

            if selection.maximum is None:
                return available

            fixed_maximum = min(len(available), max(selection.maximum, 0))
            return available[:fixed_maximum]

        # Curate
        not_downloaded = []
        not_downloaded.extend(curate_list(self.videos, config.videos))
        not_downloaded.extend(curate_list(self.livestreams, config.livestreams))
        not_downloaded.extend(curate_list(self.shorts, config.shorts))

        # Return
        return not_downloaded

    def commit(self):
        """Commits (saves) archive to path; do this once you've finished all of your transactions"""
        # Save backup
        self._backup()

        # Directories
        ui.info(f"Committing {self} to file..")
        paths = [self.path, self.path / "thumbnails", self.path / "videos"]
        for path in paths:
            if not path.exists():
                path.mkdir()

        # Config
        with open(self.path / "yark.json", "w+") as file:
            json.dump(self._to_dict(), file)

    def _parse_metadata_videos(self, kind: str, i: list, bucket: list):
        """Parses metadata for a category of video into it's bucket and tells user what's happening"""

        with ui.status(f"Parsing {kind} metadata.."):
            self._parse_metadata_videos_comp(i, bucket)

    def _parse_metadata_videos_comp(self, i: list, bucket: list):
        """Computes the actual parsing for `_parse_metadata_videos` without outputting what's happening"""
        added = 0
        updated_count = 0
        skipped_no_formats = 0

        for entry in i:
            # Skip video if there's no formats available; happens with upcoming videos/livestreams
            if "formats" not in entry or len(entry["formats"]) == 0:
                skipped_no_formats += 1
                continue

            # Updated intra-loop marker
            updated = False

            # Update video if it exists
            for video in bucket:
                if video.id == entry["id"]:
                    video.update(entry)
                    updated = True
                    updated_count += 1
                    break

            # Add new video if not
            if not updated:
                video = Video.new(entry, self)
                bucket.append(video)
                self.reporter.added.append(video)
                added += 1

        # Sort videos by newest
        bucket.sort(reverse=True)

        self._verbose(
            f"Parsed bucket: incoming={len(i)}, added={added}, updated={updated_count}, "
            f"skipped_no_formats={skipped_no_formats}, total_known={len(bucket)}"
        )

    def _report_deleted(self, videos: list):
        """Goes through a video category to report & save those which where not marked in the metadata as deleted if they're not already known to be deleted"""
        for video in videos:
            if video.deleted.current() == False and not video.known_not_deleted:
                self.reporter.deleted.append(video)
                video.deleted.update(None, True)

    def _clean_parts(self):
        """Cleans old temporary `.part` files which where stopped during download if present"""
        # Make a bucket for found files
        deletion_bucket: list[Path] = []

        # Scan through and find part files
        videos = self.path / "videos"
        for file in videos.iterdir():
            if file.suffix == ".part" or file.suffix == ".ytdl":
                deletion_bucket.append(file)

        # Print and delete if there are part files present
        if len(deletion_bucket) != 0:
            ui.info("Cleaning out previous temporary files..")
            for file in deletion_bucket:
                file.unlink()

    def _backup(self):
        """Creates a backup of the existing `yark.json` file in path as `yark.bak` with added comments"""
        # Get current archive path
        archive_path = self.path / "yark.json"

        # Skip backing up if the archive doesn't exist
        if not archive_path.exists():
            return

        # Open original archive to copy
        with open(self.path / "yark.json", "r") as file_archive:
            # Add comment information to backup file
            save = f"// Backup of a Yark archive, dated {datetime.utcnow().isoformat()}\n// Remove these comments and rename to 'yark.json' to restore\n{file_archive.read()}"

            # Save new information into a new backup
            with open(self.path / "yark.bak", "w+") as file_backup:
                file_backup.write(save)

    def configure_cookies_file(self) -> None:
        """Loads archive cookies path if a cookies.txt file exists."""
        cookies_path = self.path / "cookies.txt"
        self.cookies_file = cookies_path if cookies_path.exists() else None
        if self.cookies_file is not None:
            self._verbose(f"Using cookies file {self.cookies_file}")

    def _apply_cookie_settings(self, settings: dict[str, Any]) -> None:
        if self.cookies_file is not None:
            settings["cookiefile"] = str(self.cookies_file)

    def _verbose(self, message: str) -> None:
        if self.verbose:
            ui.info(f"[verbose] {message}")

    @staticmethod
    def _from_dict(encoded: dict, path: Path) -> Channel:
        """Decodes archive which is being loaded back up"""
        channel = Channel()
        channel.path = path
        channel.version = encoded["version"]
        channel.url = encoded["url"]
        channel.cookies_file = None
        channel.verbose = False
        channel.reporter = Reporter(channel)
        channel.videos = [
            Video._from_dict(video, channel) for video in encoded["videos"]
        ]
        channel.livestreams = [
            Video._from_dict(video, channel) for video in encoded["livestreams"]
        ]
        channel.shorts = [
            Video._from_dict(video, channel) for video in encoded["shorts"]
        ]
        channel.configure_cookies_file()
        return channel

    def _to_dict(self) -> dict:
        """Converts channel data to a dictionary to commit"""
        return {
            "version": self.version,
            "url": self.url,
            "videos": [video._to_dict() for video in self.videos],
            "livestreams": [video._to_dict() for video in self.livestreams],
            "shorts": [video._to_dict() for video in self.shorts],
        }

    def __repr__(self) -> str:
        return self.path.name


def _skip_video(
    videos: list[Video],
    reason: str,
    warning: bool = False,
) -> tuple[list[Video], Video]:
    """Skips first undownloaded video in `videos`, make sure there's at least one to skip otherwise an exception will be thrown"""
    # Find fist undownloaded video
    for ind, video in enumerate(videos):
        if not video.downloaded():
            # Tell the user we're skipping over it
            if warning:
                ui.warning(f"Skipping {video.id} ({reason})")
            else:
                ui.info(f"Skipping {video.id} ({reason})")

            # Set videos to skip over this one
            videos = videos[ind + 1 :]

            # Return the corrected list and the video found
            return videos, video

    # Shouldn't happen, see docs
    raise Exception(
        "We expected to skip a video and return it but nothing to skip was found"
    )


def _migrate_archive(
    current_version: int, expected_version: int, encoded: dict, channel_name: str
) -> dict:
    """Automatically migrates an archive from one to another by bootstrapping"""

    def migrate_step(cur: int, encoded: dict) -> dict:
        """Step in recursion to migrate from one to another, contains migration logic"""
        # Stop because we've reached the desired version
        if cur == expected_version:
            return encoded

        # From version 1 to version 2
        elif cur == 1:
            # Channel id to url
            encoded["url"] = "https://www.youtube.com/channel/" + encoded["id"]
            del encoded["id"]
            ui.warning(f"Please make sure {encoded['url']} is the correct url")

            # Empty livestreams/shorts lists
            encoded["livestreams"] = []
            encoded["shorts"] = []

        # From version 2 to version 3
        elif cur == 2:
            # Add deleted status to every video/livestream/short
            # NOTE: none is fine for new elements, just a slight bodge
            for video in encoded["videos"]:
                video["deleted"] = Element.new(Video._new_empty(), False)._to_dict()
            for video in encoded["livestreams"]:
                video["deleted"] = Element.new(Video._new_empty(), False)._to_dict()
            for video in encoded["shorts"]:
                video["deleted"] = Element.new(Video._new_empty(), False)._to_dict()

        # Unknown version
        else:
            ui.error(f"Unknown archive version v{cur} found during migration", True)
            sys.exit(1)

        # Increment version and run again until version has been reached
        cur += 1
        encoded["version"] = cur
        return migrate_step(cur, encoded)

    # Inform user of the backup process
    ui.warning(
        f"Automatically migrating archive from v{current_version} to v{expected_version}; backup saved at {channel_name}/yark.bak"
    )

    # Start recursion step
    return migrate_step(current_version, encoded)


def _err_dl(name: str, exception: DownloadError, retrying: bool):
    """Prints errors to stdout depending on what kind of download error occurred"""
    # Default message
    msg = f"Unknown error whilst downloading {name}, details below:\n{exception}"

    # Types of errors
    errors = [
        "<urlopen error [Errno 8] nodename nor servname provided, or not known>",
        "500",
        "Got error: The read operation timed out",
        "No such file or directory",
        "HTTP Error 404: Not Found",
        "<urlopen error timed out>",
    ]

    # Download errors
    if type(exception) == DownloadError:
        # Server connection
        if errors[0] in exception.msg:
            msg = "Issue connecting with YouTube's servers"

        # Server fault
        elif errors[1] in exception.msg:
            msg = "Fault with YouTube's servers"

        # Timeout
        elif errors[2] in exception.msg:
            msg = "Timed out trying to download video"

        # Video deleted whilst downloading
        elif errors[3] in exception.msg:
            msg = "Video deleted whilst downloading"

        # Channel not found, might need to retry with alternative route
        elif errors[4] in exception.msg:
            msg = "Couldn't find channel by it's id"

        # Random timeout; not sure if its user-end or youtube-end
        elif errors[5] in exception.msg:
            msg = "Timed out trying to reach YouTube"

    # Print error
    suffix = ", retrying in a few seconds.." if retrying else ""
    ui.warning("  • " + msg + suffix.ljust(40))

    # Wait if retrying, exit if failed
    if retrying:
        time.sleep(5)
    else:
        ui.error(f"  • Sorry, failed to download {name}", True)
        sys.exit(1)