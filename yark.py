from datetime import datetime
import json
from pathlib import Path
from uuid import uuid4
import youtube_dl
from termcolor import cprint
import requests
import hashlib
import sys


class Channel:
    @staticmethod
    def new(path: Path, id: str):
        """Creates a new channel"""
        # Details
        print("Creating new channel..")
        channel = Channel()
        channel.path = Path(path)
        channel.version = 1
        channel.id = id
        channel.videos = {}
        channel.reporter = Reporter(channel)

        # Commit and return
        channel._commit()
        return channel

    @staticmethod
    def load(path: Path):
        """Loads existing channel from path"""
        # Check existence
        path = Path(path)
        print(f"Loading {path.name} channel..")
        if not path.exists():
            raise Exception("Archive doesn't exist")

        # Load config
        encoded = json.load(open(path / "yark.json", "r"))

        # Decode and return
        decoded = Channel._from_dict(encoded, path)
        return decoded

    def metadata(self):
        """Queries YouTube for all channel metadata to refresh known videos"""
        # Construct downloader
        print("Downloading metadata..")
        settings = {
            "outtmpl": "%(id)s%(ext)s",
            "quiet": True,
        }
        ydl = youtube_dl.YoutubeDL(settings)
        custom = len(self.id) != 24  # TODO: better custom id detection
        url = (
            "https://www.youtube.com/" + ("channel/" if not custom else "c/") + self.id
        )

        # Get response and snip it
        res = ydl.extract_info(url, download=False)
        res = res["entries"][0]["entries"]

        # # NOTE: remove for production
        # demo = Path("demo/")
        # if not demo.exists():
        #     demo.mkdir()
        # with open("demo/dump.json", "w+") as file:
        #     json.dump(res, file)

        # Add videos
        print("Parsing metadata..")
        for entry in res:
            # Update or add new
            if entry["id"] in self.videos:
                self.videos[entry["id"]].update(entry)
            else:
                video = Video.new(entry, self)
                self.videos[entry["id"]] = video
                self.reporter.added.append(video)

        # Commit new data
        self._commit()

    def _commit(self):
        """Commits (saves) archive to path"""
        # Directories
        print(f"Committing {self} to file..")
        paths = [self.path, self.path / "thumbnails", self.path / "videos"]
        for path in paths:
            if not path.exists():
                path.mkdir()

        # Config
        with open(self.path / "yark.json", "w+") as file:
            json.dump(self._to_dict(), file)

    @staticmethod
    def _from_dict(encoded: dict, path: Path):
        """Decodes archive which is being loaded back up"""
        # Basics
        channel = Channel()
        channel.path = path
        channel.version = encoded["version"]
        channel.id = encoded["id"]
        channel.reporter = Reporter(channel)

        # Videos
        channel.videos = {}
        for id in encoded["videos"]:
            channel.videos[id] = Video._from_dict(id, encoded["videos"][id], channel)

        # Return
        return channel

    def _to_dict(self) -> dict:
        """Converts channel data to a dictionary to commit"""
        # Basics
        encoded = {"version": self.version, "id": self.id, "videos": {}}

        # Videos
        for id in self.videos:
            encoded["videos"][id] = self.videos[id]._to_dict()

        # Return
        return encoded

    def __repr__(self) -> str:
        return self.path.name


class Video:
    @staticmethod
    def new(entry: dict, channel: Channel):
        """Create new video from metadata entry"""
        video = Video()
        video.channel = channel
        video.id = entry["id"]
        video.title = Element.new(video, entry["title"])
        video.description = Element.new(video, entry["description"])
        video.views = Element.new(video, entry["view_count"])
        video.likes = Element.new(
            video, entry["like_count"] if "like_count" in entry else None
        )
        video.thumbnail = Element.new(video, Thumbnail.new(entry["thumbnail"], video))
        video.uploaded = _yt_date(entry["upload_date"])
        video.width = entry["width"]
        video.height = entry["height"]
        return video

    def update(self, entry: dict):
        """Updates video using new schema, adding a new timestamp to any changes"""
        self.title.update("title", entry["title"])
        self.description.update("description", entry["description"])
        self.views.update("view count", entry["view_count"])
        self.likes.update("like count", entry["like_count"])
        self.thumbnail.update("thumbnail", Thumbnail.new(entry["thumbnail"], self))

    @staticmethod
    def _from_dict(id: str, encoded: dict, channel: Channel):
        """Converts id and encoded dictionary to video for loading a channel"""
        video = Video()
        video.channel = channel
        video.id = id
        video.title = Element._from_dict(encoded["title"], video)
        video.description = Element._from_dict(encoded["description"], video)
        video.views = Element._from_dict(encoded["views"], video)
        video.likes = Element._from_dict(encoded["likes"], video)
        video.thumbnail = Thumbnail._from_element(encoded["thumbnail"], video)
        video.uploaded = datetime.fromisoformat(encoded["uploaded"])
        video.width = encoded["width"]
        video.height = encoded["height"]
        return video

    def _to_dict(self) -> dict:
        """Converts video information to dictionary for committing, doesn't include id"""
        return {
            "title": self.title._to_dict(),
            "description": self.description._to_dict(),
            "views": self.views._to_dict(),
            "likes": self.likes._to_dict(),
            "thumbnail": self.thumbnail._to_dict(),
            "uploaded": self.uploaded.isoformat(),
            "width": self.width,
            "height": self.height,
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
        uploaded = self.uploaded.strftime("%d, %b %Y")

        # Return
        return f"{title}  🔭{views} 👍{likes} 📅{uploaded}  📺{width}x{height}"


class Element:
    @staticmethod
    def new(video: Video, data):
        """Creates new element attached to a video"""
        element = Element()
        element.video = video
        element.inner = {datetime.utcnow(): data}
        return element

    def update(self, type: str, data, report: bool = True):
        """Updates element if it needs to be and returns self"""
        # Check if updating is needed
        has_id = hasattr(data, "id")
        current = self.current()
        if (not has_id and current != data) or (has_id and data.id != current.id):
            # Update
            self.inner[datetime.utcnow()] = data

            # Report
            self.video.channel.reporter.add_updated(type, self)

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

        # Added
        for video in self.added:
            cprint(f"  • {video}", "green")

        # Deleted
        for video in self.deleted:
            cprint(f"  • {video}", "red")

        # Updated
        for type, element in self.updated:
            colour = "cyan" if type in ["title", "description"] else "blue"
            video = f"  • {element.video}".ljust(80)
            type = f"🗿{type.capitalize()}"

            cprint(video + type, colour)

        # Nothing
        if not self.added and not self.deleted and not self.updated:
            cprint(f"  • Nothing was added or deleted", "grey")

        # Timestamp
        date = datetime.utcnow().isoformat()
        print(f"Yark – {date}")

    def add_updated(self, type: str, element: Element):
        """Tells reporter that an element has been updated"""
        self.updated.append((type, element))

    def reset(self):
        """Resets reporting values for new run"""
        self.added = []
        self.deleted = []
        self.updated = []


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


# Command-line interface
if __name__ == "__main__":
    # Help message
    HELP = "yark [options]\n\n  YouTube archiving made simple\n\nOptions:\n  new [name] [id]   Creates new archive with name and channel id\n  refresh [name]    Refreshes archive metadata, thumbnails, and videos\n\nExample:\n  $ yark new owez UCSMdm6bUYIBN0KfS2CVuEPA\n  $ yark refresh owez"

    # Get arguments
    args = sys.argv[1:]

    # No arguments
    if len(args) == 0:
        print(HELP + "\n\nException: No arguments provided", file=sys.stderr)

        sys.exit(1)

    # Help
    elif args[0] in ["help", "--help", "-h"]:
        print(HELP)
        sys.exit(0)

    # Create new
    elif args[0] == "new":
        # Bad arguments
        if len(args) < 3:
            raise Exception("Please provide an archive name and the channel id")

        # Create channel
        Channel.new(args[1], args[2])

    # Refresh
    elif args[0] == "refresh":
        # Bad arguments
        if len(args) < 2:
            raise Exception("Please provide the archive name")

        # Refresh channel
        channel = Channel.load(args[1])
        channel.metadata()
        # TODO: download
