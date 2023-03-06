"""Utility functions and classes for general use in route handlers"""

from flask import Response, request
from ..config import Config
from pathlib import Path
from .. import models
from yark.archiver.archive import Archive
from yark.archiver.video.video import Video
import logging


def error_response(msg: str, info: str | None = None, code: int = 500) -> Response:
    """Creates a standardized response for application-layer (our) errors"""
    return {"message": msg, "info": info}, code


def check_auth() -> Response | None:
    """Checks auth token provided to make sure it's the allowed admin one or returns an error response"""
    auth = request.headers.get("Authentication")
    secret = Config().ADMIN_SECRET
    if (auth is None or auth.split(" ")[-1] != secret) and secret != "dev":
        return error_response("Invalid admin token", None, 401)
    return None


def get_archive(slug: str) -> Archive | Response:
    """Gets archive from database using it's slug or returns an error response"""
    # Get archive info by slug
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


def get_specific_video(archive: Archive, id: str) -> Video | Response:
    """Gets a specific video from archive or returns an error response, abstracts over kinds"""
    # NOTE: if the archive format was relational we wouldn't have to do this;
    #       the API shouldn't be crap with `kind` because we cant search for
    #       just any video inside of the format
    if (video := archive.videos.inner.get(id)) is not None:
        return video
    elif (video := archive.livestreams.inner.get(id)) is not None:
        return video
    elif (video := archive.shorts.inner.get(id)) is not None:
        return video
    else:
        return error_response(
            "Video not found",
            f"Archive {archive} does not contain video of id {id}",
            404,
        )
