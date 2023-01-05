"""Channel and overall archive management with downloader"""

from datetime import datetime
import json
import os
from pathlib import Path
import time
from yt_dlp import YoutubeDL, DownloadError
from colorama import Style, Fore
import sys
from .reporter import Reporter
from .errors import ArchiveNotFoundException, _err_msg, VideoNotFoundException
from .video import Video, Element


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
    def __init__(self) -> None:
        self.max_videos: int = None
        self.max_livestreams: int = None
        self.max_shorts: int = None
        self.skip_download: bool = False
        self.skip_metadata: bool = False

    def submit(self):
        """Submits configuration, this has the effect of normalising maximums to 0 properly"""
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


class VideoLogger:
    @staticmethod
    def downloading(d):
        """Progress hook for video downloading"""
        # Get video's id
        id = d["info_dict"]["id"]

        # Downloading percent
        if d["status"] == "downloading":
            percent = d["_percent_str"].strip()
            print(
                Style.DIM + f"  • Downloading {id}, at {percent}.." + Style.NORMAL,
                end="\r",
            )

        # Finished a video's download
        elif d["status"] == "finished":
            print(Style.DIM + f"  • Downloaded {id}              " + Style.NORMAL)

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
    @staticmethod
    def new(path: Path, url: str):
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
    def load(path: Path):
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
        # Construct downloader
        print("Downloading metadata..")
        settings = {
            "outtmpl": "%(id)s%(ext)s",
            "logger": VideoLogger(),
        }

        # Get response and snip it
        res = None
        with YoutubeDL(settings) as ydl:
            for i in range(3):
                try:
                    res = ydl.extract_info(self.url, download=False)
                    break
                except Exception as exception:
                    # Report error
                    retrying = i != 2
                    _err_dl("metadata", exception, retrying)

                    # Print retrying message
                    if retrying:
                        print(
                            Style.DIM
                            + f"  • Retrying metadata download.."
                            + Style.RESET_ALL
                        )

        # Uncomment for saving big dumps for testing
        # with open("demo/dump.json", "w+") as file:
        #     json.dump(res, file)

        # Uncomment for loading big dumps for testing
        # res = json.load(open("demo/dump.json", "r"))

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
        self._parse_metadata("video", videos, self.videos)
        self._parse_metadata("livestream", livestreams, self.livestreams)
        self._parse_metadata("shorts", shorts, self.shorts)

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
            "outtmpl": f"{self.path}/videos/%(id)s.%(ext)s",
            "format": "best/mp4/hasvid",
            "logger": VideoLogger(),
            "progress_hooks": [VideoLogger.downloading],
        }

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
                        except Exception as exception:
                            # Video is privated or deleted
                            if (
                                "Private video" in exception.msg
                                or "This video has been removed by the uploader"
                                in exception.msg
                            ):
                                # Get list of downloaded videos
                                ldir = os.listdir(self.path / "videos")

                                # Find fist undownloaded video which will be the privated one
                                for ind, video in enumerate(not_downloaded):
                                    if not video.downloaded(ldir):
                                        # Tell the user we're skipping over it
                                        print(
                                            Style.DIM
                                            + f"  • Skipping {video.id} (deleted)"
                                            + Style.NORMAL,
                                        )

                                        # If this is a new occurrence then set it & report
                                        # This will only happen if its deleted after getting metadata, like in a dry run
                                        if video.deleted.current() == False:
                                            self.reporter.deleted.append(video)
                                            video.deleted.update(None, True)

                                        # Set curated videos to skip over this one
                                        not_downloaded = not_downloaded[ind + 1 :]

                                        # Break and start downloading again
                                        break

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

    def _curate(self, config: DownloadConfig) -> list:
        """Curate videos which aren't downloaded and return their urls"""

        def curate_list(videos: list, maximum: int) -> list:
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
                if not video.downloaded(ldir):
                    not_downloaded.append(video)

            # Return
            return not_downloaded

        # Get all videos in directory
        ldir = os.listdir(self.path / "videos")

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

    def _parse_metadata(self, kind: str, input: list, bucket: list):
        """Parses metadata for a category of video into it's bucket"""
        print(f"Parsing {kind} metadata..")
        for entry in input:
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
        # Get the path and make a bucket for found files
        video_path = f"{self.path}/videos"
        deletion_bucket = []

        # Scan through and find part files
        for file in os.listdir(video_path):
            filename = os.fsdecode(file)
            if filename.endswith(".part"):
                deletion_bucket.append(filename)

        # Print and delete if there are part files present
        if len(deletion_bucket) != 0:
            print("Cleaning out previous temporary files..")
            for filename in deletion_bucket:
                os.remove(f"{video_path}/{filename}")

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
    def _from_dict(encoded: dict, path: Path):
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
            print(
                Fore.YELLOW
                + "Please make sure "
                + encoded["url"]
                + " is the correct url"
                + Fore.RESET
            )

            # Empty livestreams/shorts lists
            encoded["livestreams"] = []
            encoded["shorts"] = []

        # From version 2 to version 3
        elif cur == 2:
            # Add deleted status to every video/livestream/short
            # NOTE: none is fine for new elements, just a slight bodge
            for video in encoded["videos"]:
                video["deleted"] = Element.new(None, False)._to_dict()
            for video in encoded["livestreams"]:
                video["deleted"] = Element.new(None, False)._to_dict()
            for video in encoded["shorts"]:
                video["deleted"] = Element.new(None, False)._to_dict()

        # Unknown version
        else:
            _err_msg(f"Unknown archive version v{cur} found during migration", True)
            sys.exit(1)

        # Increment version and run again until version has been reached
        cur += 1
        encoded["version"] = cur
        return migrate_step(cur, encoded)

    # Inform user of the backup process
    print(
        Fore.YELLOW
        + f"Automatically migrating archive from v{current_version} to v{expected_version}, a backup has been made at {channel_name}/yark.bak"
        + Fore.RESET
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
        "HTTP Erorr 404: Not Found",
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
    print(
        Fore.YELLOW + "  • " + msg + suffix.ljust(40) + Fore.RESET,
        file=sys.stderr,
    )

    # Wait if retrying, exit if failed
    if retrying:
        time.sleep(5)
    else:
        _err_msg("  • Sorry, failed to download {name}", True)
        sys.exit(1)
