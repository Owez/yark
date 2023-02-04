"""Archive CRUD route handlers"""

from flask_restful import Resource
from flask import Response
from .. import extensions

# TODO: flask marshmallow for get query <https://flask-marshmallow.readthedocs.io/en/latest/>


class ArchiveResource(Resource):
    """Archive CRUD"""

    @extensions.cache.cached(timeout=60, query_string=True)
    def get(self) -> Response:
        """Get archive information for the kind of information wanted; e.g. livestreams/videos"""
        return {"hello": "world"}
