# Standard Imports
from dataclasses import dataclass
from datetime import datetime

# Local Imports
from yark.archiving.archiver.migration import Migrator, Schema, v2
from yark.archiving.archiver.migration.v2 import ArchiveV2Schema


# External Imports


@dataclass(order=True, init=True, slots=True)
class ArchiveV1Schema(Schema):
    id: str
    videos: list['VideoInfo']


@dataclass(order=True, init=True, slots=True)
class VideoInfo:
    uploaded: datetime
    width: int
    height: int
    title: list[tuple[datetime, str]]
    description: list[tuple[datetime, str]]
    views: list[tuple[datetime, str]]
    thumbnail: list[tuple[datetime, str]]
    deleted: list[tuple[datetime, bool]]
    comments: dict
    notes: list


class V1Migrator(Migrator):

    previous_version = None
    next_version = v2.ArchiveV2Schema

    def upgrade(self, schema: ArchiveV1Schema) -> v2.ArchiveV2Schema:
        # Target id to url
        url = f"https://www.youtube.com/channel/{schema.id}"

        v2_schema = v2.ArchiveV2Schema(
            url=url,
            videos=schema.videos,
            livestreams=[],
            shorts=[]
        )

        # TODO: Move logging to somewhere proper
        """
        print(
            Fore.YELLOW
            + f"Please make sure {encoded['url']} is the correct url"
            + Fore.RESET
        )
        """

        return v2_schema

    def downgrade(self, schema: ArchiveV2Schema) -> ArchiveV1Schema:
        ...

