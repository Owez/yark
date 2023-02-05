"""Video list of some kind from general archive information"""

from marshmallow import Schema, fields


class VideoBriefSchema(Schema):
    """Brief information on a single video, enough to display it in a list"""

    id = fields.Str(required=True)
    title = fields.Str(required=True)
    uploaded = fields.DateTime(required=True)
    thumbnail_id = fields.Str(required=True)
