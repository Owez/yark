# Standard Imports
from dataclasses import dataclass

# Local Imports
from yark.archiving.archiver.migration import Schema
from yark.archiving.archiver.reporter import Reporter
from yark.archiving.archiver.video.comments import CommentAuthor
from yark.archiving.archiver.video.videos import Videos
from yark.archiving.archiver.migration import Migrator

# External Imports


@dataclass(order=True, slots=True)
class ArchiveV4Schema(Schema):
    # path: Path

    version: int
    url: str
    videos: Videos
    livestreams: Videos
    shorts: Videos
    comment_authors: dict[str, CommentAuthor]
    reporter: Reporter


class V4Migrator(Migrator):
    pass


