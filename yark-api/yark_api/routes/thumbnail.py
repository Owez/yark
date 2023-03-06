"""Thumbnail and thumbnail-centric CRUD route handlers"""

from flask_restful import Resource
from flask import Response, send_from_directory
from . import utils
from pathlib import Path
from werkzeug.exceptions import NotFound
import slugify
from yark.archiver.archive import Archive


class SpecificThumbnailResource(Resource):
    """Operations on a specific thumbnail"""

    def get(self, slug: str, thumbnail_id: str) -> Response:
        """Get a thumbnail by it's identifier"""
        # NOTE: ideally there should be cache on this but it errors out because of the send_from_directory
        #       see <https://github.com/pallets-eco/flask-caching/issues/167> for more about this

        # Get archive info
        if not isinstance((archive := utils.get_archive(slug)), Archive):
            return archive

        # Build a path to the thumbnail
        thumbnail_dir = Path(archive.path) / "images"
        thumbnail_filename = thumbnail_id + ".webp"

        # Serve the thumbnail from directory
        try:
            return send_from_directory(thumbnail_dir, thumbnail_filename)

        # Thumbnail not found
        except NotFound:
            return utils.error_response("Thumbnail not found", None, 404)
