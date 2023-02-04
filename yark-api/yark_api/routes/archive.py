"""Archive CRUD route handlers"""

from __future__ import annotations
from flask_restful import Resource
from flask import Response, request
from .. import extensions
from .. import models
from marshmallow import Schema, fields, ValidationError, validate
from enum import Enum
from marshmallow_enum import EnumField
from yark.archiver.archive import Archive
from yark.archiver.video.video import Video
from pathlib import Path
import logging
from typing import Any
from . import utils
import slugify


class ArchivePostKind(Enum):
    """Kind of creation request which is being made"""

    create = 1
    existing = 2


class ArchivePostQuerySchema(Schema):
    """Schema for defining what to do on a POST request"""

    intent = EnumField(ArchivePostKind, required=True)


class ArchivePostJsonImportSchema(Schema):
    """Schema for defining the specifics of importing an existing archive into the API"""

    slug = fields.Str(
        validate=validate.Length(min=1, max=models.ARCHIVE_MAX_SLUG), required=True
    )
    path = fields.Str(
        validate=validate.Length(min=1, max=models.ARCHIVE_MAX_PATH), required=True
    )


class ArchivePostJsonNewSchema(Schema):
    """Schema for defining the specifics of a brand new archive to create inside of JSON"""

    slug = fields.Str(
        validate=validate.Length(min=1, max=models.ARCHIVE_MAX_SLUG), required=True
    )
    path = fields.Str(
        validate=validate.Length(min=1, max=models.ARCHIVE_MAX_PATH), required=True
    )
    target = fields.Str(validate=validate.Length(min=7, max=512), required=True)


class ArchiveGetKind(Enum):
    """Specific kind of top-level information to fetch for an archive"""

    videos = 1
    livestreams = 2
    shorts = 3

    def get_list(self, archive: Archive) -> list[Video]:
        """Gets list of the videos from `archive` indicated by the current state"""
        logging.debug(
            f"Getting relevant videos list of kind {self.value} for {archive}"
        )
        match self.value:
            case 1:
                videos = archive.videos
            case 2:
                videos = archive.livestreams
            case 3:
                videos = archive.shorts
            case unknown:
                raise Exception(f"Unknown kind {unknown} for archive get kind")
        videos_list: list[Video] = videos.inner.items()
        return videos_list


class ArchiveGetQuerySchema(Schema):
    """Schema for defining which archive a user would like to retrieve"""

    slug = fields.Str(required=True)
    kind = EnumField(ArchiveGetKind, required=True)


class ArchiveResource(Resource):
    """Archive CRUD"""

    def post(self) -> Response:
        """Creates a new archive if the API owner requests to"""
        # Decode query arg to figure out intent
        try:
            schema_query = ArchivePostQuerySchema().load(request.args)
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
            schema_query = ArchiveGetQuerySchema().load(request.args)
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

        # Serialize videos of requested kind
        videos = schema_query["kind"].get_list(archive)
        return videos  # TODO: serialize class Video to json properly


def create_new_archive() -> Response:
    """Attempts to create a brand new archive and return it's information"""
    # Decode json body containing specifics
    try:
        body: dict[Any, Any] | None = request.json
        if body is None:
            return utils.error_response("Invalid body", None, 400)
        schema_body = ArchivePostJsonNewSchema().load(body)
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
    archive_info = models.Archive(slug=archive_slug, path=schema_body["path"])
    extensions.db.session.add(archive_info)
    extensions.db.session.commit()


def create_existing_archive() -> Response:
    """Attempts to create an existing archive by importing it, then returns it's information"""
    pass  # TODO
