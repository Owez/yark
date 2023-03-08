"""Note and note-centric CRUD route handlers"""

from flask_restful import Resource
from flask import Response, request
from . import utils
from yark.archiver.archive import Archive
from yark.archiver.video.video import Video
from yark.archiver.video.note import Note
from ..schemas.inputs.note import NotePostJsonSchema, NotePatchJsonSchema
from marshmallow import ValidationError


class NoteResource(Resource):
    """Operations on a general note inside of a video"""

    def post(self, slug: str, video_id: str) -> Response:
        """Create a new thumbnail attached to a video"""

        # Authenticate
        if (err := utils.check_auth()) is not None:
            return err

        # Validate the schema
        try:
            schema_body: NotePostJsonSchema = NotePostJsonSchema().load(request.json)
        except ValidationError:
            return utils.error_response("Invalid body schema", None, 400)

        # Get archive info
        if not isinstance((archive := utils.get_archive(slug)), Archive):
            return archive

        # Get the specific video
        if not isinstance(
            (video := utils.get_specific_video(archive, video_id)), Video
        ):
            return video

        # Add new note to video and commit
        new_note_body = schema_body["body"] if "body" in schema_body else None
        new_note = Note(
            video, schema_body["timestamp"], schema_body["title"], new_note_body
        )
        video.notes.append(new_note)
        archive.commit()

        # Return the new note's identifier with message
        return {"message": "Note created", "id": new_note.id}


class SpecificNoteResource(Resource):
    """Operations on a specific note inside of a video"""

    def patch(self, slug: str, video_id: str, note_id: str) -> Response:
        """Update an existing note attached to a video"""

        # Authenticate
        if (err := utils.check_auth()) is not None:
            return err

        # Validate the schema
        try:
            schema_body: NotePatchJsonSchema = NotePatchJsonSchema().load(request.json)
            if schema_body.is_empty():
                raise ValidationError()
        except ValidationError:
            return utils.error_response("Invalid body schema", None, 400)

        # Get archive info
        if not isinstance((archive := utils.get_archive(slug)), Archive):
            return archive

        # Get the specific video
        if not isinstance(
            (video := utils.get_specific_video(archive, video_id)), Video
        ):
            return video

        # Get note from video
        note = video.search(note_id)
        if note is None:
            return {"message": "Note not found"}, 404

        # Update note with new info
        print("TODO")

    def delete(self, slug: str, video_id: str, note_id: str) -> Response:
        """Delete a note attached to a video"""

        # Authenticate
        if (err := utils.check_auth()) is not None:
            return err

        # Get archive info
        if not isinstance((archive := utils.get_archive(slug)), Archive):
            return archive

        # Get the specific video
        if not isinstance(
            (video := utils.get_specific_video(archive, video_id)), Video
        ):
            return video

        # Delete note if it exists and commit
        kept_notes = list(filter(lambda n: n.id != note_id, video.notes))
        video.notes = kept_notes
        archive.commit()

        # Return a message saying it's been deleted
        return {"message": "Note deleted"}
