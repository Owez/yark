# Standard Imports
from typing import Type


# Local Imports
from yark.archiving.archiver.migration import v2, v3
from yark.archiving.archiver.migration import v1, v4
from yark.archiving.archiver.migration import Schema, Migrator
from yark.yark.utils import ARCHIVE_SCHEMA_COMPAT

# External Imports

versions: list[tuple[Type[Schema], Type[Migrator]]] = [
    (v1.ArchiveV1Schema, v1.V1Migrator),
    (v2.ArchiveV2Schema, v2.V2Migrator),
    (v3.ArchiveV3Schema, v3.V3Migrator),
    (v4.ArchiveV4Schema, v4.V4Migrator)
]


def is_latest_schema(content: dict) -> bool:
    if 'version' not in content.keys():
        raise TypeError

    return content['version'] == ARCHIVE_SCHEMA_COMPAT


def migrate_schema_version_to(to_version: int, content: dict) -> Schema:
    current_version: int = content['version']

    schema: Schema | None = None
    while True:
        if len(versions) > current_version:
            raise NotImplementedError('')

        if len(versions) > current_version + 1:
            break

        if current_version == to_version:
            break

        from_migrator = versions[current_version][1]()
        upgraded_schema = from_migrator.upgrade(schema)

        if not upgraded_schema:
            raise ValueError

        schema = upgraded_schema

        current_version += 1

    return schema


def from_latest_schema(content_dct) -> Schema:
    raise NotImplementedError

