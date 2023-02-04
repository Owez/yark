"""Archive CRUD route handlers"""

from flask_restful import Resource
from flask import Response


class ArchiveResource(Resource):
    """Archive CRUD"""

    def get(self) -> Response:
        return {"hello": "world"}
