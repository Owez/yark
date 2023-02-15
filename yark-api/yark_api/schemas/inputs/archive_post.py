"""Archive POST schemas and accessory classes"""

from enum import Enum
from marshmallow import Schema, fields, validate
from marshmallow_enum import EnumField
from ... import models


class ArchivePostKind(Enum):
    """Kind of creation request which is being made"""

    create = 1
    existing = 2


class ArchivePostQuerySchema(Schema):
    """Schema for defining what to do on a POST request"""

    intent = EnumField(ArchivePostKind, required=True)


class ArchivePostJsonImportSchema(Schema):
    """Schema for defining the specifics of importing an existing archive into the API"""

    slug = fields.Str(
        validate=validate.Length(min=1, max=models.ARCHIVE_MAX_SLUG), required=True
    )
    path = fields.Str(
        validate=validate.Length(min=1, max=models.ARCHIVE_MAX_PATH), required=True
    )


class ArchivePostJsonNewSchema(Schema):
    """Schema for defining the specifics of a brand new archive to create inside of JSON"""

    slug = fields.Str(
        validate=validate.Length(min=1, max=models.ARCHIVE_MAX_SLUG), required=True
    )
    path = fields.Str(
        validate=validate.Length(min=1, max=models.ARCHIVE_MAX_PATH), required=True
    )
    target = fields.Str(validate=validate.Length(min=7, max=512), required=True)
