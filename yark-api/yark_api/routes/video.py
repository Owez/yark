"""Video and video-centric CRUD route handlers"""

from flask_restful import Resource
from flask import Response
import logging
from . import utils
from .. import extensions
from yark.archiver.archive import Archive
from yark.archiver.video.video import Video


class SpecificVideoResource(Resource):
    """Operations on a specific video"""

    @extensions.cache.cached(timeout=120)
    def get(self, slug: str, id: str) -> Response:
        """Get specific information on a video"""
        logging.info(f"Getting information on video {id} for archive '{slug}'")

        # Get archive info
        if not isinstance((archive := utils.get_archive(slug)), Archive):
            return archive

        # Get the specific video
        if not isinstance((video := utils.get_specific_video(archive, id)), Video):
            return video

        # Serialize core video details
        # NOTE: we just dump the archive here, this could be made nicer but the archive format is already good
        #       replace this in the future if its deemed worthy
        return video._to_archive_b()
