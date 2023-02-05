"""Video list of some kind from general archive information"""

from marshmallow import Schema, fields, pre_dump
from yark.archiver.archive import Video
from typing import Any
from dataclasses import dataclass
import datetime


@dataclass
class VideoBrief:
    """Brief version of a video to convert into for the schema"""

    id: str
    title: str
    uploaded: datetime.datetime
    thumbnail_id: str


class VideoBriefSchema(Schema):
    """Brief information on a single video, enough to display it in a list"""

    id = fields.Str(required=True)
    title = fields.Str(required=True)
    uploaded = fields.DateTime(required=True)
    thumbnail_id = fields.Str(required=True)

    @pre_dump
    def to_video_brief(self, video: Video, **_: Any) -> VideoBrief:
        """Flattens elements attached to video and converts into video brief"""
        return VideoBrief(
            video.id,
            video.title.current(),
            video.uploaded,
            video.thumbnail.current().id,
        )
