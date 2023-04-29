# Standard Imports
import json
from pathlib import Path

# Local Imports
from . import archive
from . import comment_author
from . import element
from .archive import Archive
from yark.yark.archiving.archiver import migration
from yark.yark.utils import ARCHIVE_SCHEMA_COMPAT
from ...archiver.migration.abstraction import Schema

# External Imports


def from_json(content: str) -> Schema:
    content_dct = json.loads(content)

    if not migration.is_latest_schema(content_dct):
        schema = migration.migrate_schema_version_to(ARCHIVE_SCHEMA_COMPAT, content_dct)
    else:
        schema = migration.from_latest_schema(content_dct)

    return schema


def from_path(path: Path) -> Archive:
    content = path.read_text()

    match path.suffix:
        case '.json':
            return from_json(content)
        case _:
            raise NotImplementedError(f"Configuration extension format '{path.suffix}' is not supported")


