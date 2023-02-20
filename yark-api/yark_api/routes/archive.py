"""Archive and archive-centric CRUD route handlers"""

from __future__ import annotations
from ..schemas.inputs import archive_post, video_kind
from flask_restful import Resource
from flask import Response, request
from .. import extensions
from .. import models
from marshmallow import ValidationError
from pathlib import Path
import logging
from typing import Any
from . import utils
import slugify
from ..schemas.outputs import video_brief
from sqlalchemy.exc import IntegrityError
from yark.archiver.video.video import Video
from yark.archiver.archive import Archive


class ArchiveResource(Resource):
    """General archive handler for a non-specific one"""

    def post(self) -> Response:  # TODO: auth
        """Creates a new archive if the API owner requests to"""
        # Authenticate
        if (err := utils.check_auth()) is not None:
            return err

        # Decode query arg to figure out intent
        try:
            schema_query = archive_post.ArchivePostQuerySchema().load(request.args)
            logging.info(
                "Creating new archive with intent #" + str(schema_query["intent"])
            )
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


class SpecificArchiveResource(Resource):
    """Operations on a specific archive"""

    @extensions.cache.cached(timeout=60, query_string=True)
    def get(self, slug: str) -> Response:
        """Get archive information for the kind of information wanted; e.g. livestreams/videos"""
        logging.info(f"Getting existing archive with slug '{slug}'")

        # Decode query args to get kind
        try:
            schema_query = video_kind.VideoKindGetQuerySchema().load(request.args)
        except ValidationError:
            return utils.error_response("Invalid query schema", None, 400)

        # Get archive
        if not isinstance((archive := utils.get_archive(slug)), Archive):
            return archive

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

    # Say that it's been created successfully
    return {"message": "Archive created", "slug": archive_slug}


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

    # Say that it's been created successfully
    return {"message": "Archive created", "slug": archive_slug}
