"""Video and video-centric CRUD route handlers"""

from flask_restful import Resource
from flask import Response


class SpecificVideoResource(Resource):
    """Operations on a specific video"""

    def get(self, slug: str, id: str) -> Response:
        """Get specific information on a video"""
        print(slug, id)  # TODO
