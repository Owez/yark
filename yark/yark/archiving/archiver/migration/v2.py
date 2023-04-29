# Standard Imports
from dataclasses import dataclass

# Local Imports
from yark.archiving.archiver.migration import Schema, Migrator
from yark.archiving.archiver.migration import v1


# External Imports


@dataclass(order=True, slots=True)
class ArchiveV2Schema(Schema):
    url: str
    videos: list['v1.VideoInfo']
    livestreams: list[str]
    shorts: list[str]


class V2Migrator(Migrator):

    previous_version = None
    next_version = v1.ArchiveV1Schema

    def upgrade(self, schema: 'v1.ArchiveV1Schema') -> ArchiveV2Schema:
        # Target id to url
        url = f"https://www.youtube.com/channel/{schema.id}"

        v2_schema = ArchiveV2Schema(
            url=url,
            videos=schema.videos,
            livestreams=[],
            shorts=[]
        )

        return v2_schema

    def downgrade(self, schema: ArchiveV2Schema) -> v1.ArchiveV1Schema:
        ...



