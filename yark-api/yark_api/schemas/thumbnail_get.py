"""Thumbnail GET schemas and accessory classes"""

from marshmallow import Schema, fields, validate
from .. import models


class ThumbnailGetQuerySchema(Schema):
    """Schema for defining which thumbnail to retrieve for a GET request"""

    id = fields.Str(validate=validate.Length(equal=40), required=True)
    archive_slug = fields.Str(
        validate=validate.Length(min=1, max=models.ARCHIVE_MAX_SLUG), required=True
    )
