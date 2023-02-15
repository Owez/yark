"""Archive GET schemas and accessory classes"""

from enum import Enum
from yark.archiver.archive import Archive
from yark.archiver.video.video import Video
import logging
from marshmallow import Schema
from marshmallow_enum import EnumField


class VideoGetKind(Enum):
    """Specific kind of top-level information to fetch for an archive"""

    videos = 1
    livestreams = 2
    shorts = 3

    def get_list(self, archive: Archive) -> list[Video]:
        """Gets list of the videos from `archive` indicated by the current state"""
        logging.debug(
            f"Getting relevant videos list of kind {self.value} for {archive}"
        )
        match self.value:
            case 1:
                videos = archive.videos
            case 2:
                videos = archive.livestreams
            case 3:
                videos = archive.shorts
            case unknown:
                raise Exception(f"Unknown kind {unknown} for archive get kind")
        videos_list: list[Video] = videos.inner.values()
        return videos_list

    def get_specific(self, archive: Archive, id: str) -> Video | None:
        """Tries to get a specific video `id` from the provided `archive` or returns nothing"""
        logging.debug(
            f"Trying to get video {id} from {archive} in video category {self}"
        )
        match self.value:
            case 1:
                return archive.videos.inner.get(id)
            case 2:
                return archive.livestreams.inner.get(id)
            case 3:
                return archive.shorts.inner.get(id)


class VideoKindGetQuerySchema(Schema):
    """Schema for defining which archive a user would like to retrieve"""

    kind = EnumField(VideoGetKind, required=True)
