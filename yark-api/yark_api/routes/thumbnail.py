"""Thumbnail CRUD route handlers"""

from flask_restful import Resource
from flask import Response, request, send_from_directory
from ..schemas import thumbnail_get
from marshmallow import ValidationError
from . import utils
from .. import extensions, models
from pathlib import Path
from werkzeug.exceptions import NotFound


class ThumbnailResource(Resource):
    """Thumbnail CRUD"""

    @extensions.cache.cached(timeout=0, query_string=True)
    def get(self) -> Response:
        """Get a thumbnail by it's identifier"""
        # Decode query arg to get id
        try:
            schema_query = thumbnail_get.ThumbnailGetQuerySchema().load(request.args)
        except ValidationError:
            return utils.error_response("Invalid query schema", None, 400)

        # Get archive info by the provided slug
        archive_info: models.Archive | None = models.Archive.query.filter_by(
            slug=schema_query["archive_slug"]
        ).first()
        if archive_info is None:
            return utils.error_response("Archive not found", None, 404)

        # Build a path to the thumbnail
        thumbnail_dir = Path(archive_info.path) / "thumbnails"
        thumbnail_filename = schema_query["id"] + ".webp"

        # Serve the thumbnail from directory
        try:
            return send_from_directory(thumbnail_dir, thumbnail_filename)

        # Thumbnail not found
        except NotFound:
            return utils.error_response("Thumbnail not found", None, 404)
