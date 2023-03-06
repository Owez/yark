"""Note schemas and accessory classes"""

from marshmallow import Schema, fields, validate


class NotePostJsonSchema(Schema):
    """Schema for defining a new note to create"""

    title = fields.Str(validate=validate.Length(min=1, max=32), required=True)
    timestamp = fields.Integer(required=True)
    body = fields.Str(validate=validate.Length(min=1, max=4000))
