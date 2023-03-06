"""File and file-centric CRUD route handlers for videos"""

from flask_restful import Resource
from flask import Response, send_from_directory
from . import utils
from pathlib import Path
from werkzeug.exceptions import NotFound
from yark.archiver.archive import Archive


class SpecificVideoFileResource(Resource):
    """Operations on a specific video file"""

    def get(self, slug: str, video_id: str) -> Response:
        """Get a raw video file by the video's identifier"""

        # Get archive info
        if not isinstance((archive := utils.get_archive(slug)), Archive):
            return archive

        # Build a path to the raw video file
        file_dir = Path(archive.path) / "videos"
        file_filename = video_id + ".mp4"
        if not (file_dir / file_filename).exists():
            file_filename = video_id + ".webm"

        # Serve the raw video file from directory
        try:
            return send_from_directory(file_dir, file_filename)

        # Thumbnail not found
        except NotFound:
            return utils.error_response("Video file not found", None, 404)
