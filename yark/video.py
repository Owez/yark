"""Single video inside of an archive, allowing reporting and addition/updates to it's status using timestamps"""

from __future__ import annotations
from datetime import datetime
from pathlib import Path
from uuid import uuid4
import requests
import hashlib
from .errors import NoteNotFoundException
from .utils import _truncate_text
from typing import TYPE_CHECKING, Any, Optional
import multiprocessing
from functools import partial
from .config import Config

if TYPE_CHECKING:
    from .archive import Archive

IMAGE_THUMBNAIL = "webp"
"""Image extension setting for all thumbnails"""

IMAGE_AUTHOR_ICON = "jpg"
"""Image extension setting for all author icons"""


class Video:
    archive: "Archive"
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
    def new(config: Config, entry: dict[str, Any], archive: Archive) -> Video:
        """Create new video from metadata entry"""
        # Normal
        video = Video()
        video.archive = archive
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
        video.thumbnail = Element.new(
            video, Image.new(video, entry["thumbnail"], IMAGE_THUMBNAIL)
        )
        video.deleted = Element.new(video, False)
        video.comments = Comments(archive)
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
            "thumbnail", Image.new(self, entry["thumbnail"], IMAGE_THUMBNAIL)
        )
        self.deleted.update("undeleted", False)
        if config.comments and entry["comments"] is not None:
            self.comments.update(entry["comments"])

        # Runtime-only
        self.known_not_deleted = True

    def filename(self) -> Optional[str]:
        """Returns the filename for the downloaded video, if any"""
        videos = self.archive.path / "videos"
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
    def _from_dict(encoded: dict, archive: Archive) -> Video:
        """Converts id and encoded dictionary to video for loading an archive"""
        # Normal
        video = Video()
        video.archive = archive
        video.id = encoded["id"]
        video.uploaded = datetime.fromisoformat(encoded["uploaded"])
        video.width = encoded["width"]
        video.height = encoded["height"]
        video.title = Element._from_dict(encoded["title"], video)
        video.description = Element._from_dict(encoded["description"], video)
        video.views = Element._from_dict(encoded["views"], video)
        video.likes = Element._from_dict(encoded["likes"], video)
        video.thumbnail = Image._from_element(
            encoded["thumbnail"], video, IMAGE_THUMBNAIL
        )
        video.deleted = Element._from_dict(encoded["deleted"], video)
        video.comments = Comments(archive)
        video.notes = [Note._from_dict(video, note) for note in encoded["notes"]]

        # Load data
        video.comments.load_archive(encoded["comments"])

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
    parent: Video | Comment | Archive | CommentAuthor
    inner: dict[datetime, Any]

    @staticmethod
    def new(parent: Video | Comment | Archive | CommentAuthor, data):
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
                archive = (
                    self.parent.archive
                    if isinstance(self.parent, Video)
                    or isinstance(self.parent, Comment)
                    or isinstance(self.parent, CommentAuthor)
                    else self.parent  # NOTE: this can be simplified but Archive would be a circular dep
                )
                archive.reporter.add_updated(kind, self)

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
        encoded: dict, parent: Video | Comment | Archive | CommentAuthor
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


class Image:
    parent: Video | CommentAuthor
    id: str
    path: Path
    ext: str

    @staticmethod
    def new(parent: Video | CommentAuthor, url: str, ext: str) -> Image:
        """Pulls a new image from YouTube and saves"""
        # Basic details
        image = Image()
        image.parent = parent
        image.ext = ext

        # Get image and id which is a hash
        downloaded_image, image.id = _image_and_hash(url)

        # Calculate path
        image.path = image._path()

        # Save to collection
        with open(image.path, "wb+") as file:
            file.write(downloaded_image)

        # Return
        return image

    def _path(self) -> Path:
        """Returns path to current image"""
        return self.parent.archive.path / "images" / f"{self.id}.{self.ext}"

    @staticmethod
    def load(id: str, parent: Video | CommentAuthor, ext: str):
        """Loads existing image from saved path by id"""
        image = Image()
        image.id = id
        image.parent = parent
        image.ext = ext
        image.path = image._path() / f"{image.id}.{ext}"
        return image

    @staticmethod
    def _from_element(element: dict, video: Video, ext: str) -> Element:
        """Converts element of images to properly formed images"""
        decoded = Element._from_dict(element, video)
        for date in decoded.inner:
            decoded.inner[date] = Image.load(decoded.inner[date], video, ext)
        return decoded

    def _to_element(self) -> str:
        """Converts images instance to value used for element identification"""
        return self.id


def _image_and_hash(url: str) -> tuple[bytes, str]:
    """Downloads an image and calculates it's BLAKE2 hash, returning both"""
    image = requests.get(url).content
    hash = hashlib.blake2b(image, digest_size=20, usedforsecurity=False).hexdigest()
    return image, hash


class CommentAuthor:
    archive: Archive
    id: str
    name: Element
    icon: Element

    @staticmethod
    def new_or_update(
        archive: Archive, id: str, name: str, icon_url: str
    ) -> CommentAuthor:
        """Adds a new author with `name` of `id` if it doesn't exist, or tries to update `name` if it does"""
        # Get from archive
        author = archive.comment_authors.get(id)

        # Create new
        if author is None:
            author = CommentAuthor()
            author.archive = archive
            author.id = id
            author.name = Element.new(author, name)
            author.icon = Element.new(
                author, Image.new(author, icon_url, IMAGE_AUTHOR_ICON)
            )
            archive.comment_authors[id] = author

        # Update existing
        else:
            author.name.update(None, name)
            author.icon.update(None, Image.new(author, icon_url, IMAGE_AUTHOR_ICON))

        # Return
        return author

    @staticmethod
    def _from_dict_head(archive: Archive, id: str, element: dict) -> CommentAuthor:
        """Decodes from the dictionary with a head `id`, e.g. `"head": { body }`"""
        author = CommentAuthor()
        author.archive = archive
        author.id = id
        author.name = Element._from_dict(element["name"], author)
        author.icon = Element._from_dict(element["icon"], author)
        return author

    def _to_dict_head(self) -> dict:
        """Encodes comment author to the body part of a head + body, e.g. `"head": { body }`"""
        return {"name": self.name._to_dict(), "icon": self.icon._to_dict()}


class Comments:
    archive: Archive
    inner: dict[str, Comment]

    def __init__(self, archive: Archive) -> None:
        self.archive = archive
        self.inner = {}

    def load_archive(self, comments: dict[str, dict]):
        """Loads comments from a comment level in a Yark archive"""
        for id in comments.keys():
            self.inner[id] = Comment._from_dict_head(
                self.archive, None, id, comments[id]
            )

    def save_archive(self) -> dict[str, dict]:
        """Saves each comment as a dictionary inside of comments"""
        payload = {}
        for id in self.inner:
            payload[id] = self.inner[id]._to_dict_head()
        return payload

    def update(self, comments: list[dict]):
        """Updates comments according to metadata"""
        # All comments which have been found so we can see the difference to find deleted comments
        known: list[str] = []

        # List of comments which are children of the parent of `str`; we do this to guarantee we have all roots before we add children
        adoption_queue: list[tuple[str, Comment]] = []

        # Go through comments found using processing pool for images
        p = multiprocessing.Pool(16)
        p.map(
            partial(
                self._update_comment,
                known=known,
                adoption_queue=adoption_queue,
            ),
            comments,
        )

        # Add all the children to parents now we know they're all there
        for parent_id, comment in adoption_queue:
            self.inner[parent_id].children.inner[comment.id] = comment

        # Update those who have been deleted by finding the difference between recently got and archived
        for id in self.inner.keys():
            if id not in known:
                comment = self.inner[id]
                comment.deleted.update(None, True)

    def _update_comment(
        self,
        entry: dict,
        known: list[str],
        adoption_queue: list[tuple[str, Comment]],
    ):
        """Runs through the complete update procedures for one comment"""
        # Decode the identifier and possible parent; can be used to check parent
        parent_id, id = _decode_comment_id(entry["id"])

        # Add to known comments to find difference later
        known.append(id)

        # Try to update comment if it's a child
        if (
            parent_id is not None
            and parent_id in self.inner
            and id in self.inner[parent_id].children.inner
        ):
            comment = self.inner[parent_id].children.inner[id]
            comment.update(entry)

        # Try to update comment if it's a parent
        elif id in self.inner:
            comment = self.inner[id]
            comment.update(entry)

        # Create a new comment
        else:
            # Encode into a full comment with no parent no matter what
            created = datetime.fromtimestamp(entry["timestamp"])
            comment = Comment.new(
                self.archive,
                None,
                id,
                entry["author_id"],
                entry["author"],
                entry["author_thumbnail"],
                entry["text"],
                entry["is_favorited"],
                created,
            )

            # Add comment to our comments
            if parent_id is None:
                self.inner[id] = comment

            # Add to adoption queue if the comment is a child
            else:
                adoption_queue.append((parent_id, comment))


def _decode_comment_id(id: str) -> tuple[Optional[str], str]:
    """Decodes a comment id into it's top-level or parent and self"""
    if "." in id:
        got = id.split(".")
        return got[0], got[1]
    return None, id


class Comment:
    archive: Archive
    parent: Optional[Comment]
    id: str
    author: CommentAuthor
    body: Element
    favorited: Element
    deleted: Element
    created: datetime
    children: Comments

    @staticmethod
    def new(
        archive: Archive,
        parent: Optional[Comment],
        id: str,
        author_id: str,
        author_name: str,
        author_icon_url: str,
        body: str,
        favorited: bool,
        created: datetime,
    ) -> Comment:
        """Creates a new comment with simplified information inputs"""
        comment = Comment()
        comment.archive = archive
        comment.parent = parent
        comment.id = id
        comment.author = CommentAuthor.new_or_update(
            archive, author_id, author_name, author_icon_url
        )
        comment.body = Element.new(comment, body)
        comment.favorited = Element.new(comment, favorited)
        comment.deleted = Element.new(comment, False)
        comment.created = created
        comment.children = Comments(archive)
        return comment

    def update(self, entry: dict[str, Any]):
        """Updates comment using new metadata schema, adding a new timestamp to any changes and also updating it's author automatically"""
        self.author.new_or_update(
            self.archive, entry["author_id"], entry["author"], entry["author_thumbnail"]
        )
        self.body.update(None, entry["text"])
        self.favorited.update(None, entry["is_favorited"])
        self.deleted.update(None, False)

    @staticmethod
    def _from_dict_head(
        archive: Archive, parent: Optional[Comment], id: str, element: dict
    ) -> Comment:
        """Loads existing comment and it's children attached to a video dict in a head + body format"""
        # Basic
        comment = Comment()
        comment.archive = archive
        comment.parent = parent
        comment.id = id
        comment.author = archive.comment_authors[element["author_id"]]
        comment.body = Element._from_dict(element["body"], comment)
        comment.favorited = Element._from_dict(element["favorited"], comment)
        comment.deleted = Element._from_dict(element["deleted"], comment)
        comment.created = datetime.fromisoformat(element["created"])

        # Get children using head & body method
        comment.children = Comments(archive)
        for id in element["children"].keys():
            comment.children.inner[id] = Comment._from_dict_head(
                archive, comment, id, element["children"][id]
            )

        # Return
        return comment

    def _to_dict_head(self) -> dict:
        """Converts comment and it's children to dictionary representation in a head + body format"""
        # Get children using head & body method
        children = {}
        for id in self.children.inner.keys():
            children[id] = self.children.inner[id]._to_dict_head()

        # Basics
        payload = {
            "author_id": self.author.id,
            "body": self.body._to_dict(),
            "favorited": self.favorited._to_dict(),
            "deleted": self.deleted._to_dict(),
            "created": self.created.isoformat(),
            "children": children,
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
