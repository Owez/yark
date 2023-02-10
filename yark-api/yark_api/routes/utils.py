"""Utility functions and classes for general use in route handlers"""

from flask import Response, request
from ..config import Config

def error_response(msg: str, info: str | None = None, code: int = 500) -> Response:
    """Creates a standardized response for application-layer (our) errors"""
    return {"message": msg, "info": info}, code


def check_auth() -> Response | None:
    """Checks auth token provided to make sure it's the allowed admin one or returns an error response"""
    auth = request.headers.get("Authorization").split(" ")[-1]
    if auth is None or auth != Config().ADMIN_SECRET:
        return error_response("Invalid admin token", None, 401)
    return None

