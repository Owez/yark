"""File and file-centric CRUD route handlers for videos"""

from flask_restful import Resource
from flask import Response, send_from_directory
from . import utils
from .. import models
import slugify
from pathlib import Path
from werkzeug.exceptions import NotFound


class SpecificVideoFileResource(Resource):
    """Operations on a specific video file"""

    def get(self, slug: str, id: str) -> Response:
        """Get a raw video file by the video's identifier"""

        # Make the slug into a slug if it isn't already
        archive_slug = slugify.slugify(slug)

        # Get archive info by the provided slug
        archive_info: models.Archive | None = models.Archive.query.filter_by(
            slug=archive_slug
        ).first()
        if archive_info is None:
            return utils.error_response("Archive not found", None, 404)

        # Build a path to the raw video file
        file_dir = Path(archive_info.path) / "videos"
        file_filename = id + ".mp4"

        # Serve the raw video file from directory
        try:
            return send_from_directory(file_dir, file_filename)

        # Thumbnail not found
        except NotFound:
            return utils.error_response("Video file not found", None, 404)
