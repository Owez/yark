"""Note schemas and accessory classes"""

from marshmallow import Schema, fields, validate


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

    def is_empty(self) -> bool:
        """Checks if this schema is empty, when it needs to have at least one value in it"""
        return "title" not in self and "timestamp" not in self and "body" not in self
