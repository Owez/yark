from datetime import datetime
from fnmatch import fnmatch
import json
import os
from pathlib import Path
from yt_dlp import YoutubeDL
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
import flask
import threading
import webbrowser
import logging
import multiprocessing

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


#
# ARCHIVER
#


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
            raise ArchiveNotFoundException("Archive doesn't exist")

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
            "logger": VideoLogger(),
        }
        custom = len(self.id) != 24  # TODO: better custom id detection
        url = (
            "https://www.youtube.com/" + ("channel/" if not custom else "c/") + self.id
        )

        # Get response and snip it
        with YoutubeDL(settings) as ydl:
            res = ydl.extract_info(url, download=False)["entries"]

        # # NOTE: remove for production
        # demo = Path("demo/")
        # if not demo.exists():
        #     demo.mkdir()
        # with open("demo/dump.json", "w+") as file:
        #     json.dump(res, file)

        # Add videos
        print("Parsing metadata..")
        for entry in res:
            # Updated marker
            updated = False

            # Update video if it exists
            for video in self.videos:
                if video.id == entry["id"]:
                    video.update(entry)
                    updated = True

            # Add new video if not
            if not updated:
                video = Video.new(entry, self)
                self.videos.append(video)
                self.reporter.added.append(video)

        # Sort videos by newest
        self.videos.sort(reverse=True)

        # Commit new data
        self._commit()

    def download(self):
        """Downloads all videos which haven't already been downloaded"""
        # Get all videos in directory
        print("Downloading new videos..")
        ldir = os.listdir(self.path / "videos")

        # Curate
        not_downloaded = []
        for video in self.videos:
            if not video.downloaded(ldir):
                not_downloaded.append(f"https://www.youtube.com/watch?v={video.id}")

        # Download
        settings = {
            "outtmpl": f"{self.path}/videos/%(id)s.%(ext)s",
            "format": "mp4/best/hasvid",
            "logger": VideoLogger(),
            "progress_hooks": [VideoLogger.downloading],
        }
        with YoutubeDL(settings) as ydl:
            ydl.download(not_downloaded)

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
        channel = Channel()
        channel.path = path
        channel.version = encoded["version"]
        channel.id = encoded["id"]
        channel.reporter = Reporter(channel)
        channel.videos = [
            Video._from_dict(video, channel) for video in encoded["videos"]
        ]
        return channel

    def _to_dict(self) -> dict:
        """Converts channel data to a dictionary to commit"""
        return {
            "version": self.version,
            "id": self.id,
            "videos": [video._to_dict() for video in self.videos],
        }

    def __repr__(self) -> str:
        return self.path.name


class VideoLogger:
    @staticmethod
    def downloading(d):
        """Progress hook for video downloading"""
        # Get video's id
        id = d["info_dict"]["id"]

        # Downloading percent
        if d["status"] == "downloading":
            percent = d["_percent_str"].strip()
            print(Style.DIM, f" • Downloading {id}, at {percent}..", end="\r")

        # Finished a video's download
        elif d["status"] == "finished":
            print(Style.DIM, f" • Downloaded {id}              ", end="\r")
            print(Style.RESET_ALL)

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
        print(msg)


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
        self.likes.update(
            "like count", entry["like_count"] if "like_count" in entry else None
        )
        self.thumbnail.update("thumbnail", Thumbnail.new(entry["thumbnail"], self))

    def downloaded(self, ldir: list) -> bool:
        """Checks if this video has been downloaded"""
        # Try to find id in videos
        for file in ldir:
            if fnmatch(file, f"{self.id}*"):
                return True

        # No matches
        return False

    def updated(self) -> bool:
        """Checks if this video's title or description have been updated"""
        return len(self.title.inner) > 1 or len(self.description.inner) > 1

    @staticmethod
    def _from_dict(encoded: dict, channel: Channel):
        """Converts id and encoded dictionary to video for loading a channel"""
        video = Video()
        video.channel = channel
        video.id = encoded["id"]
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
            "id": self.id,
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

    def __lt__(self, other) -> bool:
        return self.uploaded < other.uploaded


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
            print(Fore.GREEN + f"  • {video}")

        # Deleted
        for video in self.deleted:
            print(Fore.RED + f"  • {video}")

        # Updated
        for type, element in self.updated:
            colour = Fore.CYAN if type in ["title", "description"] else Fore.BLUE
            video = f"  • {element.video}".ljust(80)
            type = f"🗿{type.capitalize()}"

            print(colour + video + type)

        # Nothing
        if not self.added and not self.deleted and not self.updated:
            print(Style.DIM, f"  • Nothing was added or deleted")

        # Timestamp
        date = datetime.utcnow().isoformat()
        print(Style.RESET_ALL + f"Yark – {date}")

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
            error = request.args["error"] if "error" in request.args else None
            return render_template("index.html", error=error)

    @app.route("/channel/<name>")
    def channel(name):
        """Channel information"""
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

    @app.route("/channel/<name>/<id>")
    def video(name, id):
        """Detailed video information and viewer"""
        try:
            channel = Channel.load(name)
            video = channel.videos[id]
            title = f"{name} – {video.title.current().lower()}"
            views_data = json.dumps(video.views._to_dict())
            likes_data = json.dumps(video.likes._to_dict())
            return render_template(
                "video.html",
                title=title,
                video=video,
                views_data=views_data,
                likes_data=likes_data,
            )
        except ArchiveNotFoundException:
            return redirect(url_for("index", error="Couldn't open channel's archive"))
        except Exception as e:
            return redirect(url_for("index", error=f"Internal server error:\n{e}"))

    @app.route("/archive/<path:target>")
    def archive(target):
        """Serves archive files"""
        return send_from_directory("", target)

    return app


#
# CLI
#

if __name__ == "__main__":
    # Help message
    HELP = "yark [options]\n\n  YouTube archiving made simple.\n\nOptions:\n  new [name] [id]   Creates new archive with name and channel id\n  refresh [name]    Refreshes archive metadata, thumbnails, and videos\n  view [name?]      Launches viewer website for channel\n\nExample:\n  $ yark new owez UCSMdm6bUYIBN0KfS2CVuEPA\n  $ yark refresh owez\n  $ yark view owez"

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
        channel.download()
        channel.reporter.print()

    # View
    elif args[0] == "view":
        # Get and start app
        app = viewer()
        threading.Thread(
            target=lambda: app.run(host="127.0.0.1", port=7667, debug=False)
        ).start()

        # Start on channel name
        if len(args) > 1:
            # Get name
            channel = args[1]
            print(f"Starting viewer for {channel}..")
            webbrowser.open(f"http://127.0.0.1:7667/channel/{channel}")

        # Start on channel finder
        else:
            print("Starting viewer..")
            webbrowser.open(f"http://127.0.0.1:7667/")
