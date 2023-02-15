"""Utility functions and classes for general use in route handlers"""

from flask import Response, request
from ..config import Config
from pathlib import Path
from .. import models
from yark.archiver.archive import Archive
import logging


def error_response(msg: str, info: str | None = None, code: int = 500) -> Response:
    """Creates a standardized response for application-layer (our) errors"""
    return {"message": msg, "info": info}, code


def check_auth() -> Response | None:
    """Checks auth token provided to make sure it's the allowed admin one or returns an error response"""
    auth = request.headers.get("Authorization")
    if auth is None or auth.split(" ")[-1] != Config().ADMIN_SECRET:
        return error_response("Invalid admin token", None, 401)
    return None


def get_archive(slug: str) -> Archive | Response:
    """Gets archive from database using it's slug or returns an error response"""
    # Get archive by slug
    archive_info: models.Archive | None = models.Archive.query.filter_by(
        slug=slug
    ).first()

    # Return 404 if it doesn't exist
    if archive_info is None:
        return error_response("Archive not found", None, 404)
    
    # Open archive
    try:
        archive_path = Path(archive_info.path)
        return Archive.load(archive_path)
    except Exception as e:
        logging.error(f"Archive directory for {slug} not found!")
        return error_response(
            "Archive seems to be deleted",
            "Archive is known about but it's data could not be found. The archive directory/file might've been moved or deleted by accident. This isn't your fault if you're a user.",
            404,
        )
