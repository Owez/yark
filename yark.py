from datetime import datetime
from fnmatch import fnmatch
import json
import os
from pathlib import Path
import time
from uuid import uuid4
from yt_dlp import YoutubeDL, DownloadError
import colorama
from colorama import Style, Fore
import requests
import hashlib
import sys
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
)
import threading
import webbrowser
import logging
import urllib3
from importlib.metadata import version

#
# COLORAMA
#

colorama.init()

#
# EXCEPTIONS
#


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


#
# CONSTANTS
#

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

#
# ARCHIVER
#


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
                Style.DIM,
                f" • Downloading {id}, at {percent}.." + Style.NORMAL,
                end="\r",
            )

        # Finished a video's download
        elif d["status"] == "finished":
            print(Style.DIM, f" • Downloaded {id}              " + Style.NORMAL)

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


class Maximums:
    def __init__(self) -> None:
        self.videos: int = None
        self.livestreams: int = None
        self.shorts: int = None

    def submit(self):
        """Sets other categories to 0 if one maximum is defined"""
        no_maximums = (
            self.videos is None and self.livestreams is None and self.shorts is None
        )
        if not no_maximums:
            if self.videos is None:
                self.videos = 0
            if self.livestreams is None:
                self.livestreams = 0
            if self.shorts is None:
                self.shorts = 0


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
                    _dl_error("metadata", exception, retrying)

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
                    _msg_err(f"Unknown video kind '{kind}' found", True)

        # Parse metadata
        self._parse_metadata("video", videos, self.videos)
        self._parse_metadata("livestream", livestreams, self.livestreams)
        self._parse_metadata("shorts", shorts, self.shorts)

        # Go through each and report deleted
        self._report_deleted(self.videos)
        self._report_deleted(self.livestreams)
        self._report_deleted(self.shorts)

    def download(self, maximums: Maximums):
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
                    not_downloaded = self._curate(maximums)

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
                                            Style.DIM,
                                            f" • Skipping {video.id} (deleted)"
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
                    _dl_error("videos", exception, i != 4)

    def search(self, id: str):
        """Searches channel for a video with the corresponding `id` and returns"""
        # Search
        for video in self.videos:
            if video.id == id:
                return video

        # Raise exception if it's not found
        raise VideoNotFoundException(f"Couldn't find {id} inside archive")

    def _curate(self, maximums: Maximums) -> list:
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
        not_downloaded.extend(curate_list(self.videos, maximums.videos))
        not_downloaded.extend(curate_list(self.livestreams, maximums.livestreams))
        not_downloaded.extend(curate_list(self.shorts, maximums.shorts))

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


class Video:
    @staticmethod
    def new(entry: dict, channel: Channel):
        """Create new video from metadata entry"""
        # Normal
        video = Video()
        video.channel = channel
        video.id = entry["id"]
        video.uploaded = _yt_date(entry["upload_date"])
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

    def downloaded(self, ldir: list) -> bool:
        """Checks if this video has been downloaded"""
        # Try to find id in videos
        for file in ldir:
            if fnmatch(file, f"{self.id}.mp4"):
                return True

        # No matches
        return False

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
    def _from_dict(encoded: dict, channel: Channel):
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
        truncate = 31
        title = self.title.current()
        if len(title) > truncate:
            title = title[: truncate - 2] + ".."
        title = title.ljust(truncate)

        # Views and likes
        views = _magnitude(self.views.current()).ljust(6)
        likes = _magnitude(self.likes.current()).ljust(6)

        # Width and height
        width = self.width if self.width is not None else "?"
        height = self.height if self.height is not None else "?"

        # Upload date
        uploaded = self.uploaded.strftime("%d %b %Y")

        # Return
        return f"{title}  🔎{views} │ 👍{likes} │ 📅{uploaded} │ 📺{width}x{height}"

    def __lt__(self, other) -> bool:
        return self.uploaded < other.uploaded


class Element:
    @staticmethod
    def new(video: Video, data):
        """Creates new element attached to a video with some initial data"""
        element = Element()
        element.video = video
        element.inner = {datetime.utcnow(): data}
        return element

    def update(self, kind: str, data):
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

    @staticmethod
    def _from_dict(encoded: dict, video: Video):
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
        element = Element._from_dict(element, video)
        for date in element.inner:
            element.inner[date] = Thumbnail.load(element.inner[date], video)
        return element

    def _to_element(self) -> str:
        """Converts thumbnail instance to value used for element identification"""
        return self.id


class Note:
    """Allows Yark users to add notes to videos"""

    @staticmethod
    def new(video: Video, timestamp: int, title: str, body: str = None):
        """Creates a new note"""
        note = Note()
        note.video = video
        note.id = str(uuid4())
        note.timestamp = timestamp
        note.title = title
        note.body = body
        return note

    @staticmethod
    def _from_dict(video: Video, element: dict):
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
# REPORTING
#


class Reporter:
    def __init__(self, channel: Channel) -> None:
        self.channel = channel
        self.added = []
        self.deleted = []
        self.updated = []

    def print(self):
        """Prints coloured report to STDOUT"""
        # Initial message
        print(f"Report for {self.channel} channel:")

        # Updated
        for type, element in self.updated:
            colour = (
                Fore.CYAN
                if type in ["title", "description", "undeleted"]
                else Fore.BLUE
            )
            video = f"  • {element.video}".ljust(82)
            type = f" │ 🔥{type.capitalize()}"

            print(colour + video + type)

        # Added
        for video in self.added:
            print(Fore.GREEN + f"  • {video}")

        # Deleted
        for video in self.deleted:
            print(Fore.RED + f"  • {video}")

        # Nothing
        if not self.added and not self.deleted and not self.updated:
            print(Style.DIM, f"  • Nothing was added or deleted")

        # Timestamp
        date = datetime.utcnow().isoformat()
        print(Style.RESET_ALL + f"Yark – {date}")

    def add_updated(self, kind: str, element: Element):
        """Tells reporter that an element has been updated"""
        self.updated.append((kind, element))

    def reset(self):
        """Resets reporting values for new run"""
        self.added = []
        self.deleted = []
        self.updated = []


#
# UTILS
#


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
            _msg_err(f"Unknown archive version v{cur} found during migration", True)
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


def _magnitude(count: int = None) -> str:
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


def _yt_date(input: str) -> datetime:
    """Decodes date from YouTube like `20180915` for example"""
    return datetime.strptime(input, "%Y%m%d")


def _parse_timestamp(input: str) -> int:
    """Parses timestamp into seconds or raises `TimestampException`"""
    # Check existence
    input = input.strip()
    if input == "":
        raise TimestampException("No input provided")

    # Split colons
    splitted = input.split(":")
    splitted.reverse()
    if len(splitted) > 3:
        raise TimestampException("Days and onwards aren't supported")

    # Parse
    secs = 0
    try:
        # Seconds
        secs += int(splitted[0])

        # Minutes
        if len(splitted) > 1:
            secs += int(splitted[1]) * 60

        # Hours
        if len(splitted) > 2:
            secs += int(splitted[2]) * 60 * 60
    except:
        raise TimestampException("Only numbers are allowed in timestamps")

    # Return
    return secs


def _fmt_timestamp(timestamp: int) -> str:
    """Formats previously parsed timestamp"""
    # Collector
    parts = []

    # Hours
    if timestamp >= 60 * 60:
        # Get hours float then append truncated
        hours = timestamp / (60 * 60)
        parts.append(str(int(hours)).rjust(2, "0"))

        # Remove truncated hours from timestamp
        timestamp = int((hours - int(hours)) * 60 * 60)

    # Minutes
    if timestamp >= 60:
        # Get minutes float then append truncated
        minutes = timestamp / 60
        parts.append(str(int(minutes)).rjust(2, "0"))

        # Remove truncated minutes from timestamp
        timestamp = int((minutes - int(minutes)) * 60)

    # Seconds
    if len(parts) == 0:
        parts.append("00")
    parts.append(str(timestamp).rjust(2, "0"))

    # Return
    return ":".join(parts)


def _dl_error(name: str, exception: DownloadError, retrying: bool):
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
        _msg_err("  • Sorry, failed to download {name}", True)
        sys.exit(1)


def _archive_not_found():
    """Errors out the user if the archive doesn't exist"""
    _msg_err("Archive doesn't exist, please make sure you typed it's name correctly!")
    sys.exit(1)


def _pypi_version():
    """Checks if there's a new version of Yark and tells the user if it's significant"""
    # Get package data from PyPI
    http = urllib3.PoolManager()
    req = http.request("GET", "https://pypi.org/pypi/yark/json")
    data = json.loads(req.data.decode("utf-8"))

    def decode_version(version: str) -> tuple:
        """Decodes stringified versioning into a tuple"""
        return tuple([int(v) for v in version.split(".")[:2]])

    # Generate versions
    our_major, our_minor = decode_version(version("yark"))
    their_major, their_minor = decode_version(data["info"]["version"])

    # Compare versions
    if their_major > our_major:
        print(
            Fore.YELLOW
            + f"There's a major update for Yark ready to download! Run `pip3 install --upgrade yark`"
            + Fore.RESET
        )
    elif their_minor > our_minor:
        print(
            f"There's a small update for Yark ready to download! Run `pip3 install --upgrade yark`"
        )


def _msg_err(msg: str, report_msg: bool = False):
    """Provides a red-coloured error message to the user in the STDERR pipe"""
    msg = (
        msg
        if not report_msg
        else f"{msg}\nPlease file a bug report if you think this is a problem with Yark!"
    )
    print(Fore.RED + Style.BRIGHT + msg + Style.NORMAL + Fore.RESET, file=sys.stderr)


#
# VIEWER
#


def viewer() -> Flask:
    """Generates viewer flask app, launch by just using the typical `app.run()`"""
    # Make flask app
    app = Flask(__name__)

    # Only log errors
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    # Routing
    @app.route("/", methods=["POST", "GET"])
    def index():
        """Open channel for non-selected channel"""
        # Redirect to requested channel
        if request.method == "POST":
            name = request.form["channel"]
            return redirect(url_for("channel", name=name))

        # Show page
        elif request.method == "GET":
            visited = request.cookies.get("visited")
            if visited is not None:
                visited = json.loads(visited)
            error = request.args["error"] if "error" in request.args else None
            return render_template("index.html", error=error, visited=visited)

    @app.route("/channel/<name>")
    def channel_empty(name):
        """Empty channel url, just redirect to videos by default"""
        return redirect(url_for("channel", name=name, kind="videos"))

    @app.route("/channel/<name>/<kind>")
    def channel(name, kind):
        """Channel information"""
        if kind not in ["videos", "livestreams", "shorts"]:
            return redirect(url_for("index", error="Video kind not recognised"))

        try:
            channel = Channel.load(name)
            ldir = os.listdir(channel.path / "videos")
            return render_template(
                "channel.html", title=name, channel=channel, name=name, ldir=ldir
            )
        except ArchiveNotFoundException:
            return redirect(url_for("index", error="Couldn't open channel's archive"))
        except Exception as e:
            return redirect(url_for("index", error=f"Internal server error:\n{e}"))

    @app.route(
        "/channel/<name>/<kind>/<id>", methods=["GET", "POST", "PATCH", "DELETE"]
    )
    def video(name, kind, id):
        """Detailed video information and viewer"""
        if kind not in ["videos", "livestreams", "shorts"]:
            return redirect(
                url_for("channel", name=name, error="Video kind not recognised")
            )

        try:
            # Get information
            channel = Channel.load(name)
            video = channel.search(id)

            # Return video webpage
            if request.method == "GET":
                title = f"{video.title.current()} · {name}"
                views_data = json.dumps(video.views._to_dict())
                likes_data = json.dumps(video.likes._to_dict())
                return render_template(
                    "video.html",
                    title=title,
                    video=video,
                    views_data=views_data,
                    likes_data=likes_data,
                )

            # Add new note
            elif request.method == "POST":
                # Parse json
                new = request.get_json()
                if not "title" in new:
                    return "Invalid schema", 400

                # Create note
                timestamp = _parse_timestamp(new["timestamp"])
                title = new["title"]
                body = new["body"] if "body" in new else None
                note = Note.new(video, timestamp, title, body)

                # Save new note
                video.notes.append(note)
                video.channel.commit()

                # Return
                return note._to_dict(), 200

            # Update existing note
            elif request.method == "PATCH":
                # Parse json
                update = request.get_json()
                if not "id" in update or (
                    not "title" in update and not "body" in update
                ):
                    return "Invalid schema", 400

                # Find note
                try:
                    note = video.search(update["id"])
                except NoteNotFoundException:
                    return "Note not found", 404

                # Update and save
                if "title" in update:
                    note.title = update["title"]
                if "body" in update:
                    note.body = update["body"]
                video.channel.commit()

                # Return
                return "Updated", 200

            # Delete existing note
            elif request.method == "DELETE":
                # Parse json
                delete = request.get_json()
                if not "id" in delete:
                    return "Invalid schema", 400

                # Filter out note with id and save
                filtered_notes = []
                for note in video.notes:
                    if note.id != delete["id"]:
                        filtered_notes.append(note)
                video.notes = filtered_notes
                video.channel.commit()

                # Return
                return "Deleted", 200

        # Archive not found
        except ArchiveNotFoundException:
            return redirect(url_for("index", error="Couldn't open channel's archive"))

        # Video not found
        except VideoNotFoundException:
            return redirect(url_for("index", error="Couldn't find video in archive"))

        # Timestamp for note was invalid
        except TimestampException:
            return "Invalid timestamp", 400

        # Unknown error
        except Exception as e:
            return redirect(url_for("index", error=f"Internal server error:\n{e}"))

    @app.route("/archive/<path:target>")
    def archive(target):
        """Serves archive files"""
        return send_from_directory(os.getcwd(), target)

    @app.template_filter("timestamp")
    def _jinja2_filter_timestamp(timestamp, fmt=None):
        """Formatter hook for timestamps"""
        return _fmt_timestamp(timestamp)

    return app


#
# CLI
#


def run():
    """Command-line-interface launcher"""
    # Help message
    HELP = f"yark [options]\n\n  YouTube archiving made simple.\n\nOptions:\n  new [name] [url]            Creates new archive with name and channel url\n  refresh [name] [args?]   Refreshes/downloads archive with optional config\n  view [name?]                Launches offiline archive viewer website\n\nExample:\n  $ yark new owez https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA\n  $ yark refresh owez\n  $ yark view owez"

    def no_help():
        """Prints out help message and exits, displaying a 'no additional help' message"""
        print(HELP)
        print("\nThere's no additional help for this command")
        sys.exit(0)

    # Get arguments
    args = sys.argv[1:]

    # No arguments
    if len(args) == 0:
        print(HELP, file=sys.stderr)
        _msg_err(f"\nError: No arguments provided")
        sys.exit(1)

    # Version announcements before going further
    try:
        _pypi_version()
    except Exception as err:
        _msg_err(
            f"Error: Failed to check for new Yark version, info:\n"
            + Style.NORMAL
            + str(err)
            + Style.BRIGHT,
            True,
        )

    # Help
    if args[0] in ["help", "--help", "-h"]:
        print(HELP)
        sys.exit(0)

    # Create new
    elif args[0] == "new":
        # More help
        if len(args) == 2 and args[1] == "--help":
            no_help()

        # Bad arguments
        if len(args) < 3:
            _msg_err("Please provide an archive name and the channel url")
            sys.exit(1)

        # Create channel
        Channel.new(args[1], args[2])

    # Refresh
    elif args[0] == "refresh":
        # More help
        if len(args) == 2 and args[1] == "--help":
            print(
                f"yark refresh [name] [args?]\n\n  Refreshes/downloads archive with optional configuration.\n  If a maximum is set, unset categories won't be downloaded\n\nArguments:\n  --videos=[max]        Maximum recent videos to download\n  --shorts=[max]        Maximum recent shorts to download\n  --livestreams=[max]   Maximum recent livestreams to download\n\n Example:\n  $ yark refresh demo\n  $ yark refresh demo --videos=5\n  $ yark refresh demo --shorts=2 --livestreams=25"
            )
            sys.exit(0)

        # Bad arguments
        if len(args) < 2:
            _msg_err("Please provide the archive name")
            sys.exit(1)

        # Get maximums
        maximums = Maximums()
        if len(args) > 2:

            def parse_int(maximum: str) -> int:
                """Tries to parse a maximum integer input"""
                try:
                    return int(maximum)
                except:
                    print(HELP, file=sys.stderr)
                    _msg_err(
                        f"\nError: The value '{maximum}' isn't a valid maximum number"
                    )
                    sys.exit(1)

            # Set each maximum if provided
            for maximum in args[2:]:
                # Video maximum
                if maximum.startswith("--videos="):
                    maximums.videos = parse_int(maximum.split("=")[1])

                # Livestream maximum
                elif maximum.startswith("--livestreams="):
                    maximums.livestreams = parse_int(maximum.split("=")[1])

                # Shorts maximum
                elif maximum.startswith("--shorts="):
                    maximums.shorts = parse_int(maximum.split("=")[1])

                # Unknown argument (maximum)
                else:
                    print(HELP, file=sys.stderr)
                    _msg_err(
                        f"\nError: Unknown argument '{maximum}' provided for archive refresh"
                    )
                    sys.exit(1)

        # Submit maximums
        maximums.submit()

        # Refresh channel
        try:
            channel = Channel.load(args[1])
            channel.metadata()
            channel.download(maximums)
            channel.commit()
            channel.reporter.print()
        except ArchiveNotFoundException:
            _archive_not_found()

    # View
    elif args[0] == "view":

        def launch():
            """Launches viewer"""
            app = viewer()
            threading.Thread(target=lambda: app.run(port=7667)).run()

        # More help
        if len(args) == 2 and args[1] == "--help":
            no_help()

        # Start on channel name
        if len(args) > 1:
            # Get name
            channel = args[1]

            # Jank archive check
            if not Path(channel).exists():
                _archive_not_found()

            # Launch and start browser
            print(f"Starting viewer for {channel}..")
            webbrowser.open(f"http://127.0.0.1:7667/channel/{channel}/videos")
            launch()

        # Start on channel finder
        else:
            print("Starting viewer..")
            webbrowser.open(f"http://127.0.0.1:7667/")
            launch()

    # Unknown
    else:
        print(HELP, file=sys.stderr)
        _msg_err(f"\nError: Unknown command '{args[0]}' provided!", True)
        sys.exit(1)


if __name__ == "__main__":
    run()
