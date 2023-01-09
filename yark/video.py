"""Single video inside of a channel, allowing reporting and addition/updates to it's status using timestamps"""

from __future__ import annotations
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from uuid import uuid4
import requests
import hashlib
from .errors import NoteNotFoundException
from .utils import _truncate_text
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .channel import Channel


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
    comments: Comments

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
        video.comments = Comments(video)
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
        self.comments.update(entry["comments"])

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
        video.deleted = Element._from_dict(encoded["deleted"], video)
        video.comments = Comments(video).load_archive(encoded["comments"])
        video.notes = [Note._from_dict(video, note) for note in encoded["notes"]]

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
            "comments": self.comments.save_archive(),
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
    parent: Video | Comment | Channel | CommentAuthor
    inner: dict[datetime, Any]

    @staticmethod
    def new(parent: Video | Comment | Channel | CommentAuthor, data):
        """Creates new element attached to a video with some initial data"""
        element = Element()
        element.parent = parent
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
                channel = (
                    self.parent.channel
                    if isinstance(self.parent, Video)
                    else self.parent.video.channel
                    if isinstance(self.parent, Comment)
                    else self.parent
                    if isinstance(self.parent, Channel)
                    else self.parent.channel
                )
                channel.reporter.add_updated(kind, self)

        # Return self
        return self

    def current(self):
        """Returns most recent element"""
        return self.inner[list(self.inner.keys())[-1]]

    def changed(self) -> bool:
        """Checks if the value has ever been modified from it's original state"""
        return len(self.inner) > 1

    @staticmethod
    def _from_dict(
        encoded: dict, parent: Video | Comment | Channel | CommentAuthor
    ) -> Element:
        """Converts encoded dictionary into element"""
        # Basics
        element = Element()
        element.parent = parent
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


class CommentAuthor:
    channel: Channel
    id: str
    name: Element

    @staticmethod
    def _from_channel(channel: Channel, id: str) -> CommentAuthor:
        """Gets the comment author from the channel based on it's identifier or raises an exception"""
        found = channel.comment_authors[id]
        if found is None:
            raise Exception(f"Couldn't find comment author '{id}' expected")
        return found

    def update(self, name: str):
        """Updates values if of author if newer"""
        self.name.update(None, name)

    @staticmethod
    def _from_dict_head(channel: Channel, id: str, element: dict) -> CommentAuthor:
        """Decodes from the dictionary with a head `id`, e.g. `"head": { body }`"""
        author = CommentAuthor()
        author.channel = channel
        author.id = id
        author.name = Element._from_dict(element["name"], author)
        return author

    def _to_dict_head(self) -> dict:
        """Encodes comment author to the body part of a head + body, e.g. `"head": { body }`"""
        return {"id": self.id, "name": self.name._to_dict()}


class Comments:
    video: Video
    inner: dict[str, Comment]

    def __init__(self, video: Video) -> None:
        self.video = video
        self.inner = {}

    def load_archive(self, comments: dict[str, dict]):
        """Loads comments from Yark archive"""
        for id in comments.keys():
            self.inner[id] = Comment._from_dict_head(self.video, None, id, comments[id])

    def save_archive(self) -> dict[str, dict]:
        """Saves each comment as a dictionary inside of comments"""
        payload = {}
        for id in self.inner:
            payload[id] = self.inner[id]._to_dict_head()
        return payload

    def update(self, comments: list[dict]):
        """Updates comments according to metadata"""
        # Go through comments found
        for comment_metadata in comments:
            # Decode the identifier; can be used to check parent
            parent_id, id = _decode_comment_id(comment_metadata["id"])
            pass  # TODO


def _decode_comment_id(id: str) -> tuple[Optional[str], str]:
    """Decodes a comment id into it's top-level or parent and self"""
    if "." in id:
        got = id.split(".")
        return got[0], got[1]
    return None, id


class Comment:
    video: Video
    parent: Optional[Comment]
    id: str
    body: Element
    author: CommentAuthor
    children: dict[str, Comment]
    favorited: Element
    created: datetime

    @staticmethod
    def _from_dict_head(
        video: Video, parent: Optional[Comment], id: str, element: dict
    ) -> Comment:
        """Loads existing comment and it's children attached to a video dict in a head + body format"""
        # Basic
        comment = Comment()
        comment.video = video
        comment.parent = parent
        comment.id = id
        comment.body = Element._from_dict(element["body"], comment)
        comment.author = CommentAuthor._from_channel(
            video.channel, element["author_id"]
        )
        comment.favorited = Element._from_dict(element["favorited"], comment)
        comment.created = datetime.fromisoformat(element["created"])

        # Get children using head & body method
        for id in element["children"].keys():
            comment.children[id] = Comment._from_dict_head(
                video, comment, id, element["children"][id]
            )

        # Return
        return comment

    def _to_dict_head(self) -> dict:
        """Converts comment and it's children to dictionary representation in a head + body format"""
        # Get children using head & body method
        children = {}
        for id in self.children.keys():
            children[id] = self.children[id]._to_dict_head()

        # Basics
        payload = {
            "body": self.body._to_dict(),
            "author_id": self.author.id,
            "children": children,
            "favorited": self.favorited._to_dict(),
            "created": self.created.isoformat(),
        }

        # Return
        return payload


class Note:
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
