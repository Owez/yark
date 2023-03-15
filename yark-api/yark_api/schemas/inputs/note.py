"""Note schemas and accessory classes"""

from marshmallow import Schema, fields, validate
from typing import Any


class NotePostJsonSchema(Schema):
    """Schema for defining a new note to create"""

    title = fields.Str(validate=validate.Length(min=1, max=32), required=True)
    timestamp = fields.Integer(required=True)
    body = fields.Str(validate=validate.Length(min=1, max=4000))


class NotePatchJsonSchema(Schema):
    """Schema for updating an existing note"""

    title = fields.Str(validate=validate.Length(min=1, max=32))
    timestamp = fields.Integer()
    body = fields.Str(validate=validate.Length(min=1, max=4000))

    @staticmethod
    def is_empty(schema: dict[str, Any]) -> bool:
        """Checks if this schema is empty, when it needs to have at least one value in it"""
        return (
            "title" not in schema and "timestamp" not in schema and "body" not in schema
        )
