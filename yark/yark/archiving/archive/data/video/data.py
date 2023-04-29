"""Single video inside an archive, allowing reporting and addition/updates to it's status using timestamps"""
# Standard Imports
from datetime import datetime
from typing import Any, Optional, TYPE_CHECKING
from dataclasses import dataclass

# Local Imports
from yark.yark.archiving.archive.data.video.image import Image, image_element_from_archive
from yark.yark.exceptions import NoteNotFoundException
from yark.yark.utils import IMAGE_THUMBNAIL, truncate_text
from yark.yark.archiving.config.data import Config
from yark.yark.archiving.archive.data.element import Element
from yark.yark.archiving.archive.data.video.comments import Comments
from yark.yark.archiving.archive.data.video.note import Note
from yark.yark.utils import yt

if TYPE_CHECKING:
    from yark.yark.archiving.archive.data import Archive

# External Imports


@dataclass(init=True, slots=True)
class Video:
    archive: 'Archive'
    id: str
    uploaded: datetime
    width: int
    height: int
    title: 'Element'
    description: 'Element'
    views: 'Element'
    likes: 'Element'
    thumbnail: 'Element'
    deleted: 'Element'
    notes: list[Note]
    comments: Comments
    known_not_deleted: bool

    def update(self, config: Config, entry: dict[str, Any]) -> None:
        """Updates video using new metadata schema, adding a new timestamp to any changes"""
        # Normal
        self.title.update(("title", self), entry["title"])
        self.description.update(("description", self), entry["description"])
        self.views.update(("view count", self), entry["view_count"])
        self.likes.update(
            ("like count", self), entry["like_count"] if "like_count" in entry else None
        )
        self.thumbnail.update(
            ("thumbnail", self),
            Image.new(
                self.archive,
                entry["thumbnail"],
                IMAGE_THUMBNAIL,
            ),
        )
        self.deleted.update(("undeleted", self), False)
        if config.comments and entry["comments"] is not None:
            self.comments.update(entry["comments"])

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

    def search(self, kind: str) -> Note:
        """Searches video for note's id"""
        for note in self.notes:
            if note.id == kind:
                return note

        raise NoteNotFoundException(f"Couldn't find note {kind}")

    def url(self) -> str:
        """Returns the YouTube watch url of the current video"""
        # NOTE: livestreams and shorts are currently just videos and can be seen via a normal watch url
        return f"https://www.youtube.com/watch?v={self.id}"

    def __repr__(self) -> str:
        # Title
        title = truncate_text(self.title.current())

        # Views and likes
        views = yt._magnitude(self.views.current()).ljust(6)
        likes = yt._magnitude(self.likes.current()).ljust(6)

        # Width and height
        width = self.width if self.width is not None else "?"
        height = self.height if self.height is not None else "?"

        # Upload date
        uploaded = yt._encode_date_human(self.uploaded)

        return f"{title}  🔎{views} │ 👍{likes} │ 📅{uploaded} │ 📺{width}x{height}"

    def __lt__(self, other: 'Video') -> bool:
        return self.uploaded < other.uploaded


def from_config(config: Config, archive: 'Archive', entry: dict[str, Any]) -> Video:
    """Create new video from metadata entry"""
    video = Video(
        archive=archive,
        id=entry['id'],
        uploaded=yt._decode_date_yt(entry['upload_date']),
        width=entry['width'],
        height=entry['height'],
        title=Element.new_data(archive, entry['title']),
        description=Element.new_data(archive, entry['description']),
        views=Element.new_data(archive, entry['view_count']),
        likes=Element.new_data(archive, entry['like_count'] if 'like_count' in entry else None),
        thumbnail=Element.new_data(archive, Image.new(archive, entry["thumbnail"], IMAGE_THUMBNAIL)),
        deleted=Element.new_data(archive, False),
        comments=Comments(archive),
        notes=[],
        known_not_deleted=True
    )

    # Add comments if they're there
    if config.comments and entry["comments"] is not None:
        video.comments.update(entry["comments"])

    return video


def _from_archive_ib(archive: 'Archive', kind: str, encoded: dict[str, Any]) -> Video:
    """Converts archive body dict into a new video with an id passed in"""
    video = Video(
        archive=archive,
        id=kind,
        uploaded=datetime.fromisoformat(encoded["uploaded"]),
        width=encoded["width"],
        height=encoded["height"],
        title=Element.from_archive_o(archive, encoded["title"]),
        description=Element.from_archive_o(archive, encoded["description"]),
        views=Element.from_archive_o(archive, encoded["views"]),
        likes=Element.from_archive_o(archive, encoded["likes"]),
        thumbnail=image_element_from_archive(archive, encoded["thumbnail"], IMAGE_THUMBNAIL),
        deleted=Element.from_archive_o(archive, encoded["deleted"]),
        comments=Comments.from_archive_o(archive, encoded["comments"]),
        known_not_deleted=False
    )

    video.notes = [Note.from_archive_o(video, note) for note in encoded["notes"]]

    return video


def _to_archive_b(video: Video) -> dict[str, Any]:
    """Converts this video into a dict body for saving to the archive under an id"""
    return {
        "uploaded": video.uploaded.isoformat(),
        "width": video.width,
        "height": video.height,
        "title": video.title.to_archive_o(),
        "description": video.description.to_archive_o(),
        "views": video.views.to_archive_o(),
        "likes": video.likes.to_archive_o(),
        "thumbnail": video.thumbnail.to_archive_o(),
        "deleted": video.deleted.to_archive_o(),
        "comments": video.comments._to_archive_o(),
        "notes": [note._to_archive_o() for note in video.notes],
    }

