"""Other route handlers which don't fit into and specific group"""

from flask_restful import Resource
from flask import Response, redirect


class IndexResource(Resource):
    """Index route of the service"""

    def get(self) -> Response:
        """Redirect to the website if they try to access"""
        return redirect("https://yark.app")
