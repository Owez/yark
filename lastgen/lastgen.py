from __future__ import annotations

#
# UTILS
#


def _truncate_text(text: str, to: int = 31) -> str:
    """Truncates inputted `text` to ~32 length, adding ellipsis at the end if overflowing"""
    if len(text) > to:
        text = text[: to - 2].strip() + ".."
    return text.ljust(to)


#
# ERROR LOGIC
#

import sys


class ArchiveNotFoundException(Exception):
    """Archive couldn't be found, the name was probably incorrect"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class VideoNotFoundException(Exception):
    """Video couldn't be found, the id was probably incorrect"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NoteNotFoundException(Exception):
    """Note couldn't be found, the id was probably incorrect"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TimestampException(Exception):
    """Invalid timestamp inputted for note"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def _err_msg(msg: str, report_msg: bool = False):
    """Provides a red-coloured error message to the user in the STDERR pipe"""
    msg = (
        msg
        if not report_msg
        else f"{msg}\nPlease file a bug report if you think this is a problem with Yark!"
    )
    # LASTGEN: not using colorama
    # print(Fore.RED + Style.BRIGHT + msg + Style.NORMAL + Fore.RESET, file=sys.stderr)

    # LASTGEN: new
    print(msg, file=sys.stderr)


#
# ARCHIVE LOGIC
#

from datetime import datetime
import json
from pathlib import Path
import time
from yt_dlp import YoutubeDL, DownloadError  # type: ignore
import sys
from typing import Any
import time
from concurrent.futures import ThreadPoolExecutor
import time

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

from typing import Optional


class DownloadConfig:
    max_videos: Optional[int]
    max_livestreams: Optional[int]
    max_shorts: Optional[int]
    skip_download: bool
    skip_metadata: bool
    format: Optional[str]

    def __init__(self) -> None:
        self.max_videos = None
        self.max_livestreams = None
        self.max_shorts = None
        self.skip_download = False
        self.skip_metadata = False
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
            # LASTGEN: not using colorama
            # print(
            #     Fore.YELLOW
            #     + "Using the skip downloads option is recommended over setting maximums to 0"
            #     + Fore.RESET
            # )
            self.skip_download = True

            # LASTGEN: new
            print(
                "Using the skip downloads option is recommended over setting maximums to 0",
            )


class VideoLogger:
    @staticmethod
    def downloading(d):
        """Progress hook for video downloading"""
        # Get video's id
        id = d["info_dict"]["id"]

        # Downloading percent
        if d["status"] == "downloading":
            percent = d["_percent_str"].strip()
            # LASTGEN: not using colorama
            # print(
            #     Style.DIM
            #     + f"  • Downloading {id}, at {percent}..                "
            #     + Style.NORMAL,
            #     end="\r",
            # )

            # LASTGEN: new
            print(
                f"  • Downloading {id}, at {percent}..                ",
                end="\r",
            )

        # Finished a video's download
        elif d["status"] == "finished":
            # LASTGEN: not using colorama
            # print(Style.DIM + f"  • Downloaded {id}        " + Style.NORMAL)

            # LASTGEN: new
            print(f"  • Downloaded {id}        ")

    def debug(self, msg):
        """Debug log messages, ignored"""
        pass

    def info(self, msg):
        """Info log messages ignored"""
        pass

    def warning(self, msg):
        """Warning log messages ignored"""
        pass

    def error(self, msg):
        """Error log messages"""
        pass


class Channel:
    path: Path
    version: int
    url: str
    videos: list[Video]
    livestreams: list[Video]
    shorts: list[Video]
    reporter: Reporter

    @staticmethod
    def new(path: Path, url: str) -> Channel:
        """Creates a new channel"""
        # Details
        print("Creating new channel..")
        channel = Channel()
        channel.path = Path(path)
        channel.version = ARCHIVE_COMPAT
        channel.url = url
        channel.videos = []
        channel.livestreams = []
        channel.shorts = []
        channel.reporter = Reporter(channel)

        # Commit and return
        channel.commit()
        return channel

    @staticmethod
    def _new_empty() -> Channel:
        return Channel.new(
            Path("pretend"), "https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA"
        )

    @staticmethod
    def load(path: Path) -> Channel:
        """Loads existing channel from path"""
        # Check existence
        path = Path(path)
        channel_name = path.name
        print(f"Loading {channel_name} channel..")
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

    def metadata(self):
        """Queries YouTube for all channel metadata to refresh known videos"""
        # Print loading progress at the start without loading indicator so theres always a print
        msg = "Downloading metadata.."
        print(msg, end="\r")

        # Download metadata and give the user a spinner bar
        with ThreadPoolExecutor() as ex:
            # LASTGEN: not using progress
            # # Make future for downloading metadata
            # future = ex.submit(self._download_metadata)

            # LASTGEN: not using progress
            # # Start spinning
            # with PieSpinner(f"{msg} ") as bar:
            #     # Don't show bar for 2 seconds but check if future is done
            #     no_bar_time = time.time() + 2
            #     while time.time() < no_bar_time:
            #         if future.done():
            #             break
            #         time.sleep(0.25)

            #     # Show loading spinner
            #     while not future.done():
            #         bar.next()
            #         time.sleep(0.075)

            # LASTGEN: not using progress
            # # Get result from thread now that it's finished
            # res = future.result()

            # LASTGEN: updated
            res = self._download_metadata()

        # Uncomment for saving big dumps for testing
        # with open(self.path / "dump.json", "w+") as file:
        #     json.dump(res, file)

        # Uncomment for loading big dumps for testing
        # res = json.load(open(self.path / "dump.json", "r"))

        # Parse downloaded metadata
        self._parse_metadata(res)

    def _download_metadata(self) -> dict[str, Any]:
        """Downloads metadata dict and returns for further parsing"""
        # Construct downloader
        settings = {
            # Centralized logging system; makes output fully quiet
            "logger": VideoLogger(),
            # Skip downloading pending livestreams (#60 <https://github.com/Owez/yark/issues/60>)
            "ignore_no_formats_error": True,
            # Concurrent fragment downloading for increased resilience (#109 <https://github.com/Owez/yark/issues/109>)
            "concurrent_fragment_downloads": 8,
        }

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
                        # LASTGEN: not using colorama
                        # print(
                        #     Style.DIM
                        #     + f"  • Retrying metadata download.."
                        #     + Style.RESET_ALL
                        # )  # TODO: compat with loading bar

                        # LASTGEN: new
                        print(
                            f"  • Retrying metadata download.."
                        )  # TODO: compat with loading bar

    def _parse_metadata(self, res: dict[str, Any]):
        """Parses entirety of downloaded metadata"""
        # Normalize into types of videos
        videos = []
        livestreams = []
        shorts = []
        if "entries" not in res["entries"][0]:
            # Videos only
            videos = res["entries"]
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
                    _err_msg(f"Unknown video kind '{kind}' found", True)

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
        # Clean out old part files
        self._clean_parts()

        # Create settings for the downloader
        settings = {
            # Set the output path
            "outtmpl": f"{self.path}/videos/%(id)s.%(ext)s",
            # Centralized logger hook for ignoring all stdout
            "logger": VideoLogger(),
            # Logger hook for download progress
            "progress_hooks": [VideoLogger.downloading],
        }
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
                        print(f"Downloading {fmt_num}..")

                    # Continuously try to download after private/deleted videos are found
                    # This block gives the downloader all the curated videos and skips/reports deleted videos by filtering their exceptions
                    while True:
                        # Download from curated list then exit the optimistic loop
                        try:
                            urls = [video.url() for video in not_downloaded]
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
                    # Get around carriage return
                    if i == 0:
                        print()

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

        def curate_list(videos: list[Video], maximum: Optional[int]) -> list[Video]:
            """Curates the videos inside of the provided `videos` list to it's local maximum"""
            # Cut available videos to maximum if present for deterministic getting
            if maximum is not None:
                # Fix the maximum to the length so we don't try to get more than there is
                fixed_maximum = min(max(len(videos) - 1, 0), maximum)

                # Set the available videos to this fixed maximum
                new_videos = []
                for ind in range(fixed_maximum):
                    new_videos.append(videos[ind])
                videos = new_videos

            # Find undownloaded videos in available list
            not_downloaded = []
            for video in videos:
                if not video.downloaded():
                    not_downloaded.append(video)

            # Return
            return not_downloaded

        # Curate
        not_downloaded = []
        not_downloaded.extend(curate_list(self.videos, config.max_videos))
        not_downloaded.extend(curate_list(self.livestreams, config.max_livestreams))
        not_downloaded.extend(curate_list(self.shorts, config.max_shorts))

        # Return
        return not_downloaded

    def commit(self):
        """Commits (saves) archive to path; do this once you've finished all of your transactions"""
        # Save backup
        self._backup()

        # Directories
        print(f"Committing {self} to file..")
        paths = [self.path, self.path / "thumbnails", self.path / "videos"]
        for path in paths:
            if not path.exists():
                path.mkdir()

        # Config
        with open(self.path / "yark.json", "w+") as file:
            json.dump(self._to_dict(), file)

    def _parse_metadata_videos(self, kind: str, i: list, bucket: list):
        """Parses metadata for a category of video into it's bucket and tells user what's happening"""

        # Print at the start without loading indicator so theres always a print
        msg = f"Parsing {kind} metadata.."
        print(msg, end="\r")

        # Start computing and show loading spinner
        with ThreadPoolExecutor() as ex:
            # LASTGEN: not using progress
            # # Make future for computation of the video list
            # future = ex.submit(self._parse_metadata_videos_comp, i, bucket)

            # LASTGEN: not using progress
            # # Start spinning
            # with PieSpinner(f"{msg} ") as bar:
            #     # Don't show bar for 2 seconds but check if future is done
            #     no_bar_time = time.time() + 2
            #     while time.time() < no_bar_time:
            #         if future.done():
            #             return
            #         time.sleep(0.25)

            #     # Spin until future is done
            #     while not future.done():
            #         time.sleep(0.075)
            #         bar.next()

            # LASTGEN: new code
            self._parse_metadata_videos_comp(i, bucket)

    def _parse_metadata_videos_comp(self, i: list, bucket: list):
        """Computes the actual parsing for `_parse_metadata_videos` without outputting what's happening"""
        for entry in i:
            # Skip video if there's no formats available; happens with upcoming videos/livestreams
            if "formats" not in entry or len(entry["formats"]) == 0:
                continue

            # Updated intra-loop marker
            updated = False

            # Update video if it exists
            for video in bucket:
                if video.id == entry["id"]:
                    video.update(entry)
                    updated = True
                    break

            # Add new video if not
            if not updated:
                video = Video.new(entry, self)
                bucket.append(video)
                self.reporter.added.append(video)

        # Sort videos by newest
        bucket.sort(reverse=True)

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
            print("Cleaning out previous temporary files..")
            for file in deletion_bucket:
                file.unlink()

    def _backup(self):
        """Creates a backup of the existing `yark.json` file in path as `yark.bak` with added comments"""
        # Get current archive path
        ARCHIVE_PATH = self.path / "yark.json"

        # Skip backing up if the archive doesn't exist
        if not ARCHIVE_PATH.exists():
            return

        # Open original archive to copy
        with open(self.path / "yark.json", "r") as file_archive:
            # Add comment information to backup file
            save = f"// Backup of a Yark archive, dated {datetime.utcnow().isoformat()}\n// Remove these comments and rename to 'yark.json' to restore\n{file_archive.read()}"

            # Save new information into a new backup
            with open(self.path / "yark.bak", "w+") as file_backup:
                file_backup.write(save)

    @staticmethod
    def _from_dict(encoded: dict, path: Path) -> Channel:
        """Decodes archive which is being loaded back up"""
        channel = Channel()
        channel.path = path
        channel.version = encoded["version"]
        channel.url = encoded["url"]
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
                # LASTGEN: not using colorama
                # print(
                #     Fore.YELLOW + f"  • Skipping {video.id} ({reason})" + Fore.RESET,
                #     file=sys.stderr,
                # )

                # LASTGEN: new
                print(
                    f"  • Skipping {video.id} ({reason})",
                    file=sys.stderr,
                )
            else:
                # LASTGEN: not using colorama
                # print(
                #     Style.DIM + f"  • Skipping {video.id} ({reason})" + Style.NORMAL,
                # )

                # LASTGEN: new
                print(
                    f"  • Skipping {video.id} ({reason})",
                    file=sys.stderr,
                )

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
    """Automatically migrates an archive from one version to another by bootstrapping"""

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
            # LASTGEN: not using colorama
            # print(
            #     Fore.YELLOW
            #     + "Please make sure "
            #     + encoded["url"]
            #     + " is the correct url"
            #     + Fore.RESET
            # )

            # LASTGEN: new
            print(+"Please make sure " + encoded["url"] + " is the correct url")

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
            _err_msg(f"Unknown archive version v{cur} found during migration", True)
            sys.exit(1)

        # Increment version and run again until version has been reached
        cur += 1
        encoded["version"] = cur
        return migrate_step(cur, encoded)

    # Inform user of the backup process
    # LASTGEN: not using colorama
    # print(
    #     Fore.YELLOW
    #     + f"Automatically migrating archive from v{current_version} to v{expected_version}, a backup has been made at {channel_name}/yark.bak"
    #     + Fore.RESET
    # )

    # LASTGEN: new
    print(
        f"Automatically migrating archive from v{current_version} to v{expected_version}, a backup has been made at {channel_name}/yark.bak"
    )

    # Start recursion step
    return migrate_step(current_version, encoded)


def _err_dl(name: str, exception: DownloadError, retrying: bool):
    """Prints errors to stdout depending on what kind of download error occurred"""
    # Default message
    msg = f"Unknown error whilst downloading {name}, details below:\n{exception}"

    # Types of errors
    ERRORS = [
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
        if ERRORS[0] in exception.msg:
            msg = "Issue connecting with YouTube's servers"

        # Server fault
        elif ERRORS[1] in exception.msg:
            msg = "Fault with YouTube's servers"

        # Timeout
        elif ERRORS[2] in exception.msg:
            msg = "Timed out trying to download video"

        # Video deleted whilst downloading
        elif ERRORS[3] in exception.msg:
            msg = "Video deleted whilst downloading"

        # Channel not found, might need to retry with alternative route
        elif ERRORS[4] in exception.msg:
            msg = "Couldn't find channel by it's id"

        # Random timeout; not sure if its user-end or youtube-end
        elif ERRORS[5] in exception.msg:
            msg = "Timed out trying to reach YouTube"

    # Print error
    suffix = ", retrying in a few seconds.." if retrying else ""
    # LASTGEN: not using colorama
    # print(
    #     Fore.YELLOW + "  • " + msg + suffix.ljust(40) + Fore.RESET,
    #     file=sys.stderr,
    # )

    # LASTGEN: new
    print(
        "  • " + msg + suffix.ljust(40),
        file=sys.stderr,
    )

    # Wait if retrying, exit if failed
    if retrying:
        time.sleep(5)
    else:
        _err_msg("  • Sorry, failed to download {name}", True)
        sys.exit(1)


#
# VIDEO LOGIC
#

from datetime import datetime
from pathlib import Path
from uuid import uuid4
import requests
import hashlib
from typing import TYPE_CHECKING, Any, Optional


class Video:
    channel: "Channel"
    id: str
    uploaded: datetime
    width: int
    height: int
    title: "Element"
    description: "Element"
    views: "Element"
    likes: "Element"
    thumbnail: "Element"
    deleted: "Element"
    notes: list["Note"]

    @staticmethod
    def new(entry: dict[str, Any], channel) -> Video:
        """Create new video from metadata entry"""
        # Normal
        video = Video()
        video.channel = channel
        video.id = entry["id"]
        video.uploaded = _decode_date_yt(entry["upload_date"])
        video.width = entry["width"]
        video.height = entry["height"]
        video.title = Element.new(video, entry["title"])
        video.description = Element.new(video, entry["description"])
        video.views = Element.new(video, entry["view_count"])
        video.likes = Element.new(
            video, entry["like_count"] if "like_count" in entry else None
        )
        video.thumbnail = Element.new(video, Thumbnail.new(entry["thumbnail"], video))
        video.deleted = Element.new(video, False)
        video.notes = []

        # Runtime-only
        video.known_not_deleted = True

        # Return
        return video

    @staticmethod
    def _new_empty() -> Video:
        fake_entry = {"hi": True}  # TODO: finish
        return Video.new(fake_entry, Channel._new_empty())

    def update(self, entry: dict):
        """Updates video using new schema, adding a new timestamp to any changes"""
        # Normal
        self.title.update("title", entry["title"])
        self.description.update("description", entry["description"])
        self.views.update("view count", entry["view_count"])
        self.likes.update(
            "like count", entry["like_count"] if "like_count" in entry else None
        )
        self.thumbnail.update("thumbnail", Thumbnail.new(entry["thumbnail"], self))
        self.deleted.update("undeleted", False)

        # Runtime-only
        self.known_not_deleted = True

    def filename(self) -> Optional[str]:
        """Returns the filename for the downloaded video, if any"""
        videos = self.channel.path / "videos"
        for file in videos.iterdir():
            if file.stem == self.id and file.suffix != ".part":
                return file.name
        return None

    def downloaded(self) -> bool:
        """Checks if this video has been downloaded"""
        return self.filename() is not None

    def updated(self) -> bool:
        """Checks if this video's title or description or deleted status have been ever updated"""
        return (
            len(self.title.inner) > 1
            or len(self.description.inner) > 1
            or len(self.deleted.inner) > 1
        )

    def search(self, id: str):
        """Searches video for note's id"""
        for note in self.notes:
            if note.id == id:
                return note
        raise NoteNotFoundException(f"Couldn't find note {id}")

    def url(self) -> str:
        """Returns the YouTube watch url of the current video"""
        # NOTE: livestreams and shorts are currently just videos and can be seen via a normal watch url
        return f"https://www.youtube.com/watch?v={self.id}"

    @staticmethod
    def _from_dict(encoded: dict, channel) -> Video:
        """Converts id and encoded dictionary to video for loading a channel"""
        # Normal
        video = Video()
        video.channel = channel
        video.id = encoded["id"]
        video.uploaded = datetime.fromisoformat(encoded["uploaded"])
        video.width = encoded["width"]
        video.height = encoded["height"]
        video.title = Element._from_dict(encoded["title"], video)
        video.description = Element._from_dict(encoded["description"], video)
        video.views = Element._from_dict(encoded["views"], video)
        video.likes = Element._from_dict(encoded["likes"], video)
        video.thumbnail = Thumbnail._from_element(encoded["thumbnail"], video)
        video.notes = [Note._from_dict(video, note) for note in encoded["notes"]]
        video.deleted = Element._from_dict(encoded["deleted"], video)

        # Runtime-only
        video.known_not_deleted = False

        # Return
        return video

    def _to_dict(self) -> dict:
        """Converts video information to dictionary for committing, doesn't include id"""
        return {
            "id": self.id,
            "uploaded": self.uploaded.isoformat(),
            "width": self.width,
            "height": self.height,
            "title": self.title._to_dict(),
            "description": self.description._to_dict(),
            "views": self.views._to_dict(),
            "likes": self.likes._to_dict(),
            "thumbnail": self.thumbnail._to_dict(),
            "deleted": self.deleted._to_dict(),
            "notes": [note._to_dict() for note in self.notes],
        }

    def __repr__(self) -> str:
        # Title
        title = _truncate_text(self.title.current())

        # Views and likes
        views = _magnitude(self.views.current()).ljust(6)
        likes = _magnitude(self.likes.current()).ljust(6)

        # Width and height
        width = self.width if self.width is not None else "?"
        height = self.height if self.height is not None else "?"

        # Upload date
        uploaded = _encode_date_human(self.uploaded)

        # Return
        return f"{title}  🔎{views} │ 👍{likes} │ 📅{uploaded} │ 📺{width}x{height}"

    def __lt__(self, other) -> bool:
        return self.uploaded < other.uploaded


def _decode_date_yt(input: str) -> datetime:
    """Decodes date from YouTube like `20180915` for example"""
    return datetime.strptime(input, "%Y%m%d")


def _encode_date_human(input: datetime) -> str:
    """Encodes an `input` date into a standardized human-readable format"""
    return input.strftime("%d %b %Y")


def _magnitude(count: Optional[int] = None) -> str:
    """Displays an integer as a sort of ordinal order of magnitude"""
    if count is None:
        return "?"
    elif count < 1000:
        return str(count)
    elif count < 1000000:
        value = "{:.1f}".format(float(count) / 1000.0)
        return value + "k"
    elif count < 1000000000:
        value = "{:.1f}".format(float(count) / 1000000.0)
        return value + "m"
    else:
        value = "{:.1f}".format(float(count) / 1000000000.0)
        return value + "b"


class Element:
    video: Video
    inner: dict[datetime, Any]

    @staticmethod
    def new(video: Video, data):
        """Creates new element attached to a video with some initial data"""
        element = Element()
        element.video = video
        element.inner = {datetime.utcnow(): data}
        return element

    def update(self, kind: Optional[str], data):
        """Updates element if it needs to be and returns self, reports change unless `kind` is none"""
        # Check if updating is needed
        has_id = hasattr(data, "id")
        current = self.current()
        if (not has_id and current != data) or (has_id and data.id != current.id):
            # Update
            self.inner[datetime.utcnow()] = data

            # Report if wanted
            if kind is not None:
                self.video.channel.reporter.add_updated(kind, self)

        # Return self
        return self

    def current(self):
        """Returns most recent element"""
        return self.inner[list(self.inner.keys())[-1]]

    def changed(self) -> bool:
        """Checks if the value has ever been modified from it's original state"""
        return len(self.inner) > 1

    @staticmethod
    def _from_dict(encoded: dict, video: Video) -> Element:
        """Converts encoded dictionary into element"""
        # Basics
        element = Element()
        element.video = video
        element.inner = {}

        # Inner elements
        for key in encoded:
            date = datetime.fromisoformat(key)
            element.inner[date] = encoded[key]

        # Return
        return element

    def _to_dict(self) -> dict:
        """Converts element to dictionary for committing"""
        # Convert each item
        encoded = {}
        for date in self.inner:
            # Convert element value if method available to support custom
            data = self.inner[date]
            data = data._to_element() if hasattr(data, "_to_element") else data

            # Add encoded data to iso-formatted string date
            encoded[date.isoformat()] = data

        # Return
        return encoded


class Thumbnail:
    video: Video
    id: str
    path: Path

    @staticmethod
    def new(url: str, video: Video):
        """Pulls a new thumbnail from YouTube and saves"""
        # Details
        thumbnail = Thumbnail()
        thumbnail.video = video

        # Get image and calculate it's hash
        image = requests.get(url).content
        thumbnail.id = hashlib.blake2b(
            image, digest_size=20, usedforsecurity=False
        ).hexdigest()

        # Calculate paths
        thumbnails = thumbnail._path()
        thumbnail.path = thumbnails / f"{thumbnail.id}.webp"

        # Save to collection
        with open(thumbnail.path, "wb+") as file:
            file.write(image)

        # Return
        return thumbnail

    @staticmethod
    def load(id: str, video: Video):
        """Loads existing thumbnail from saved path by id"""
        thumbnail = Thumbnail()
        thumbnail.id = id
        thumbnail.video = video
        thumbnail.path = thumbnail._path() / f"{thumbnail.id}.webp"
        return thumbnail

    def _path(self) -> Path:
        """Gets root path of thumbnail using video's channel path"""
        return self.video.channel.path / "thumbnails"

    @staticmethod
    def _from_element(element: dict, video: Video) -> Element:
        """Converts element of thumbnails to properly formed thumbnails"""
        decoded = Element._from_dict(element, video)
        for date in decoded.inner:
            decoded.inner[date] = Thumbnail.load(decoded.inner[date], video)
        return decoded

    def _to_element(self) -> str:
        """Converts thumbnail instance to value used for element identification"""
        return self.id


class Note:
    """Allows Yark users to add notes to videos"""

    video: Video
    id: str
    timestamp: int
    title: str
    body: Optional[str]

    @staticmethod
    def new(video: Video, timestamp: int, title: str, body: Optional[str] = None):
        """Creates a new note"""
        note = Note()
        note.video = video
        note.id = str(uuid4())
        note.timestamp = timestamp
        note.title = title
        note.body = body
        return note

    @staticmethod
    def _from_dict(video: Video, element: dict) -> Note:
        """Loads existing note attached to a video dict"""
        note = Note()
        note.video = video
        note.id = element["id"]
        note.timestamp = element["timestamp"]
        note.title = element["title"]
        note.body = element["body"]
        return note

    def _to_dict(self) -> dict:
        """Converts note to dictionary representation"""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "title": self.title,
            "body": self.body,
        }


#
# REPORTER LOGIC
#

import datetime
from typing import TYPE_CHECKING, Optional


class Reporter:
    channel: "Channel"
    added: list[Video]
    deleted: list[Video]
    updated: list[tuple[str, Element]]

    def __init__(self, channel) -> None:
        self.channel = channel
        self.added = []
        self.deleted = []
        self.updated = []

    def print(self):
        """Prints coloured report to STDOUT"""
        # Initial message
        print(f"Report for {self.channel}:")

        # Updated
        for kind, element in self.updated:
            # LASTGEN: not using colorama
            # colour = (
            #     Fore.CYAN
            #     if kind in ["title", "description", "undeleted"]
            #     else Fore.BLUE
            # )
            video = f"  • {element.video}".ljust(82)
            kind = f" │ 🔥{kind.capitalize()}"

            # LASTGEN: not using colorama
            # print(colour + video + kind)

            # LASTGEN: new
            print(video + kind)

        # Added
        for video in self.added:
            # LASTGEN: not using colorama
            # print(Fore.GREEN + f"  • {video}")

            # LASTGEN: new
            print(f"  • New: {video}")

        # Deleted
        for video in self.deleted:
            # LASTGEN: not using colorama
            # print(Fore.RED + f"  • {video}")

            # LASTGEN: new
            print(f"  • Deleted: {video}")

        # Nothing
        if not self.added and not self.deleted and not self.updated:
            # LASTGEN: not using colorama
            # print(Style.DIM + f"  • Nothing was added or deleted")

            # LASTGEN: new
            print(f"  • Nothing was added or deleted")

        # Watermark
        print(_watermark())

    def add_updated(self, kind: str, element: Element):
        """Tells reporter that an element has been updated"""
        self.updated.append((kind, element))

    def reset(self):
        """Resets reporting values for new run"""
        self.added = []
        self.deleted = []
        self.updated = []

    def interesting_changes(self):
        """Reports on the most interesting changes for the channel linked to this reporter"""

        def fmt_video(kind: str, video: Video) -> str:
            """Formats a video if it's interesting, otherwise returns an empty string"""
            # Skip formatting because it's got nothing of note
            if (
                not video.title.changed()
                and not video.description.changed()
                and not video.deleted.changed()
            ):
                return ""

            # Lambdas for easy buffer addition for next block
            buf: list[str] = []
            maybe_capitalize = lambda word: word.capitalize() if len(buf) == 0 else word
            # LASTGEN: not using colorama
            # add_buf = lambda name, change, colour: buf.append(
            #     colour + maybe_capitalize(name) + f" x{change}" + Fore.RESET
            # )

            # LASTGEN: new
            add_buf = lambda name, change: buf.append(
                maybe_capitalize(name) + f" x{change}"
            )

            # Figure out how many changes have happened in each category and format them together
            change_deleted = sum(
                1 for value in video.deleted.inner.values() if value == True
            )
            if change_deleted != 0:
                # LASTGEN: not using colorama
                # add_buf("deleted", change_deleted, Fore.RED)

                # LASTGEN: new
                add_buf("deleted", change_deleted)

            change_description = len(video.description.inner) - 1
            if change_description != 0:
                # LASTGEN: not using colorama
                # add_buf("description", change_description, Fore.CYAN)

                # LASTGEN: new
                add_buf("description", change_description)

            change_title = len(video.title.inner) - 1
            if change_title != 0:
                # LASTGEN: not using colorama
                # add_buf("title", change_title, Fore.CYAN)

                # LASTGEN: new
                add_buf("title", change_title)

            # Combine the detected changes together and capitalize
            # LASTGEN: not using colorama
            # changes = ", ".join(buf) + Fore.RESET

            # LASTGEN: new
            changes = ", ".join(buf)

            # Truncate title, get viewer link, and format all together with viewer link
            title = _truncate_text(video.title.current(), 51).strip()
            url = f"http://127.0.0.1:7667/channel/{video.channel}/{kind}/{video.id}"
            # LASTGEN: not using colorama
            # return (
            #     f"  • {title}\n    {changes}\n    "
            #     + Style.DIM
            #     + url
            #     + Style.RESET_ALL
            #     + "\n"
            # )

            # LASTGEN: new
            return f"  • {title}\n    {changes}\n    {url}\n"

        def fmt_category(kind: str, videos: list) -> Optional[str]:
            """Returns formatted string for an entire category of `videos` inputted or returns nothing"""
            # Add interesting videos to buffer
            HEADING = f"Interesting {kind}:\n"
            buf = HEADING
            for video in videos:
                buf += fmt_video(kind, video)

            # Return depending on if the buf is just the heading
            return None if buf == HEADING else buf[:-1]

        # Tell users whats happening
        print(f"Finding interesting changes in {self.channel}..")

        # Get reports on the three categories
        categories = [
            ("videos", fmt_category("videos", self.channel.videos)),
            ("livestreams", fmt_category("livestreams", self.channel.livestreams)),
            ("shorts", fmt_category("shorts", self.channel.shorts)),
        ]

        # Combine those with nothing of note and print out interesting
        not_of_note = []
        for name, buf in categories:
            if buf is None:
                not_of_note.append(name)
            else:
                print(buf)

        # Print out those with nothing of note at the end
        if len(not_of_note) != 0:
            not_of_note = "/".join(not_of_note)
            print(f"No interesting {not_of_note} found")

        # Watermark
        print(_watermark())


def _watermark() -> str:
    """Returns a new watermark with a Yark timestamp"""
    date = datetime.datetime.utcnow().isoformat()
    # LASTGEN: not using colorama
    # return Style.RESET_ALL + f"Yark – {date}"

    # LASTGEN: new
    return f"Yark – {date}"
