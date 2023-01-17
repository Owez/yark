"""Single video inside of an archive, allowing reporting and addition/updates to it's status using timestamps"""

from __future__ import annotations
from datetime import datetime
from ...errors import NoteNotFoundException
from ...utils import _truncate_text
from typing import Any, Optional
from ..config import Config
from .comments import Comments
from .element import Element
from .image import Image
from .note import Note
from ..parent import Parent

IMAGE_THUMBNAIL = "webp"
"""Image extension setting for all thumbnails"""


class Video:
    parent: Parent
    id: str
    uploaded: datetime
    width: int
    height: int
    title: Element
    description: Element
    views: Element
    likes: Element
    thumbnail: Element
    deleted: Element
    notes: list[Note]
    comments: Comments

    @staticmethod
    def new(config: Config, parent: Parent, entry: dict[str, Any]) -> Video:
        """Create new video from metadata entry"""
        # Initiate video
        video = Video()

        # Make parent for reuse in children elements
        video_parent = Parent.new_video(parent.archive, video)

        # Normal
        video.parent = parent
        video.id = entry["id"]
        video.uploaded = _decode_date_yt(entry["upload_date"])
        video.width = entry["width"]
        video.height = entry["height"]
        video.title = Element.new(video_parent, entry["title"])
        video.description = Element.new(video_parent, entry["description"])
        video.views = Element.new(video_parent, entry["view_count"])
        video.likes = Element.new(
            video_parent, entry["like_count"] if "like_count" in entry else None
        )
        video.thumbnail = Element.new_subparent(
            video_parent,
            lambda e: Image.new(
                Parent.new_element(e.parent.archive, e),
                entry["thumbnail"],
                IMAGE_THUMBNAIL,
            ),
        )
        video.deleted = Element.new(video_parent, False)
        video.comments = Comments(video_parent)
        video.notes = []

        # Add comments if they're there
        if config.comments and entry["comments"] is not None:
            video.comments.update(entry["comments"])

        # Runtime-only
        video.known_not_deleted = True

        # Return
        return video

    @staticmethod
    def _new_empty() -> Video:
        """Returns a phantom video for use in places where videos are required but we don't have a video"""
        return Video()

    def update(self, config: Config, entry: dict):
        """Updates video using new metadata schema, adding a new timestamp to any changes"""
        # Normal
        self.title.update("title", entry["title"])
        self.description.update("description", entry["description"])
        self.views.update("view count", entry["view_count"])
        self.likes.update(
            "like count", entry["like_count"] if "like_count" in entry else None
        )
        self.thumbnail.update(
            "thumbnail",
            Image.new(
                Parent.new_element(self.parent.archive, self.thumbnail),
                entry["thumbnail"],
                IMAGE_THUMBNAIL,
            ),
        )
        self.deleted.update("undeleted", False)
        if config.comments and entry["comments"] is not None:
            self.comments.update(entry["comments"])

        # Runtime-only
        self.known_not_deleted = True

    def filename(self) -> Optional[str]:
        """Returns the filename for the downloaded video, if any"""
        videos = self.parent.archive.path / "videos"
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
    def _from_archive_ib(parent: Parent, id: str, encoded: dict) -> Video:
        """Converts archive body dict into a new video with an id passed in"""
        # Initiate video
        video = Video()

        # Make parent for reuse in children elements
        video_parent = Parent.new_video(parent.archive, video)

        # Normal
        video.parent = parent
        video.id = id
        video.uploaded = datetime.fromisoformat(encoded["uploaded"])
        video.width = encoded["width"]
        video.height = encoded["height"]
        video.title = Element._from_archive_o(encoded["title"], video_parent)
        video.description = Element._from_archive_o(
            encoded["description"], video_parent
        )
        video.views = Element._from_archive_o(encoded["views"], video_parent)
        video.likes = Element._from_archive_o(encoded["likes"], video_parent)
        video.thumbnail = Image._from_element(
            encoded["thumbnail"], video_parent, IMAGE_THUMBNAIL
        )
        video.deleted = Element._from_archive_o(encoded["deleted"], video_parent)
        video.comments = Comments._from_archive_o(video_parent, encoded["comments"])
        video.notes = [
            Note._from_archive_o(video_parent, note) for note in encoded["notes"]
        ]

        # Runtime-only
        video.known_not_deleted = False

        # Return
        return video

    def _to_archive_b(self) -> dict:
        """Converts this video into a dict body for saving to the archive under an id"""
        return {
            "uploaded": self.uploaded.isoformat(),
            "width": self.width,
            "height": self.height,
            "title": self.title._to_archive_o(),
            "description": self.description._to_archive_o(),
            "views": self.views._to_archive_o(),
            "likes": self.likes._to_archive_o(),
            "thumbnail": self.thumbnail._to_archive_o(),
            "deleted": self.deleted._to_archive_o(),
            "comments": self.comments._to_archive_o(),
            "notes": [note._to_archive_o() for note in self.notes],
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


class Videos:
    parent: Parent
    inner: dict[str, Video]

    def __init__(self, parent: Parent) -> None:
        self.archive = parent
        self.inner = {}

    def sort(self):
        """Sorts `inner` videos content by newest date uploaded"""
        sorted_kv = sorted(
            self.inner.items(), key=lambda item: item[1].uploaded, reverse=True
        )
        sorted_dict = {k: v for k, v in sorted_kv}
        self.inner = sorted_dict

    @staticmethod
    def _from_archive_o(parent: Parent, videos: dict[str, dict]):
        """Loads videos from it's object in the archive"""
        output = Videos(parent)
        for id in videos.keys():
            output.inner[id] = Video._from_archive_ib(
                Parent.new_archive(parent.archive), id, videos[id]
            )
        return output

    def _to_archive_o(self) -> dict[str, dict]:
        """Saves each video as an id & body style dict inside of a videos object"""
        payload = {}
        for id in self.inner:
            payload[id] = self.inner[id]._to_archive_b()
        return payload
