"""Utility functions and classes for general use in route handlers"""

from flask import Response


def error_response(msg: str, info: str | None = None, code: int = 500) -> Response:
    """Creates a standardized response for application-layer (our) errors"""
    return {"message": msg, "info": info}, code
