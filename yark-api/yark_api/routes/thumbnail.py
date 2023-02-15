"""Thumbnail and thumbnail-centric CRUD route handlers"""

from flask_restful import Resource
from flask import Response, send_from_directory
from . import utils
from .. import models
from pathlib import Path
from werkzeug.exceptions import NotFound
import slugify


class SpecificThumbnailResource(Resource):
    """Operations on a specific thumbnail"""

    def get(self, slug: str, id: str) -> Response:
        """Get a thumbnail by it's identifier"""
        # NOTE: ideally there should be cache on this but it errors out because of the send_from_directory
        #       see <https://github.com/pallets-eco/flask-caching/issues/167> for more about this

        # Make the slug into a slug if it isn't already
        archive_slug = slugify.slugify(slug)

        # Get archive info by the provided slug
        archive_info: models.Archive | None = models.Archive.query.filter_by(
            slug=archive_slug
        ).first()
        if archive_info is None:
            return utils.error_response("Archive not found", None, 404)

        # Build a path to the thumbnail
        thumbnail_dir = Path(archive_info.path) / "images"
        thumbnail_filename = id + ".webp"

        # Serve the thumbnail from directory
        try:
            return send_from_directory(thumbnail_dir, thumbnail_filename)

        # Thumbnail not found
        except NotFound:
            return utils.error_response("Thumbnail not found", None, 404)
