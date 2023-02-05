"""Archive CRUD route handlers"""

from __future__ import annotations
from flask_restful import Resource
from flask import Response, request
from .. import extensions
from .. import models
from marshmallow import ValidationError
from yark.archiver.archive import Archive
from pathlib import Path
import logging
from typing import Any
from . import utils
import slugify
from ..schemas import archive_post, archive_get, video_brief
from sqlalchemy.exc import IntegrityError
from yark.archiver.video.video import Video


class ArchiveResource(Resource):
    """Archive CRUD"""

    def post(self) -> Response:  # TODO: auth
        """Creates a new archive if the API owner requests to"""
        # Decode query arg to figure out intent
        try:
            schema_query = archive_post.ArchivePostQuerySchema().load(request.args)
        except ValidationError:
            return utils.error_response("Invalid query schema", None, 400)

        # Branch out depending on intent
        match schema_query["intent"].value:
            case 1:
                return create_new_archive()
            case 2:
                return create_existing_archive()
            case unknown:
                raise Exception(f"Unknown kind {unknown} for archive post intent")

    @extensions.cache.cached(timeout=60, query_string=True)
    def get(self) -> Response:
        """Get archive information for the kind of information wanted; e.g. livestreams/videos"""
        # Decode query args
        try:
            schema_query = archive_get.ArchiveGetQuerySchema().load(request.args)
            logging.info(
                "Getting existing archive with slug '" + schema_query["slug"] + "'"
            )
        except ValidationError:
            return utils.error_response("Invalid query schema", None, 400)

        # Get archive by slug
        archive_info: models.Archive | None = models.Archive.query.filter_by(
            slug=schema_query["slug"]
        ).first()

        # Return 404 if it doesn't exist
        if archive_info is None:
            return utils.error_response("Archive not found", None, 404)

        # Open archive
        archive_path = Path(archive_info.path)
        archive = Archive.load(archive_path)

        # Serialize video list
        videos: list[Video] = schema_query["kind"].get_list(archive)
        return video_brief.VideoBriefSchema(many=True).dump(videos)


def create_new_archive() -> Response:
    """Attempts to create a brand new archive and return it's information"""
    # Decode json body containing specifics
    try:
        body: dict[Any, Any] | None = request.json
        if body is None:
            return utils.error_response("Invalid body", None, 400)
        schema_body = archive_post.ArchivePostJsonNewSchema().load(body)

    # Invalid json body
    except ValidationError:
        return utils.error_response("Invalid body", None, 400)

    # Create new archive and save it
    try:
        Archive(Path(schema_body["path"]), schema_body["target"]).commit()
    except Exception as e:
        return utils.error_response("Failed to create archive", str(e))

    # Make the slug into a slug if it isn't already
    archive_slug = slugify.slugify(schema_body["slug"])

    # Add to database
    try:
        archive_info = models.Archive(slug=archive_slug, path=schema_body["path"])
        extensions.db.session.add(archive_info)
        extensions.db.session.commit()

    # Slug already exists
    except IntegrityError as e:
        return utils.error_response("Slug already exists", str(e), 400)

    # Provide id to hook onto later
    return {"id": archive_info.id}


def create_existing_archive() -> Response:
    """Attempts to create an existing archive by importing it, then returns it's information"""
    # TODO: merge with create_new_archive logic throughout this function, theyre basically the same

    # Decode json body containing specifics
    try:
        body: dict[Any, Any] | None = request.json
        if body is None:
            return utils.error_response("Invalid body", None, 400)
        schema_body = archive_post.ArchivePostJsonImportSchema().load(body)

    # Invalid json body
    except ValidationError:
        return utils.error_response("Invalid body", None, 400)

    # Make the slug into a slug if it isn't already
    archive_slug = slugify.slugify(schema_body["slug"])

    # Add to database
    try:
        archive_info = models.Archive(slug=archive_slug, path=schema_body["path"])
        extensions.db.session.add(archive_info)
        extensions.db.session.commit()

    # Slug already exists
    except IntegrityError as e:
        return utils.error_response("Slug already exists", str(e), 400)

    # Provide id to hook onto later
    return {"id": archive_info.id}
