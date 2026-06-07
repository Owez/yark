"""Flask routes for the offline archive viewer."""

import json
import os
from pathlib import Path

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from ..core import Channel, Note
from ..errors import (
    ArchiveNotFoundException,
    NoteNotFoundException,
    TimestampException,
    VideoNotFoundException,
)
from .timestamps import _decode_timestamp

routes = Blueprint("routes", __name__)


def _discover_archives(
    root: Path, max_depth: int = 3, max_results: int = 50
) -> list[str]:
    """Discover archive directories containing yark.json from the current launch root."""
    discovered: list[str] = []
    skip_dirs = {".git", "__pycache__", ".venv", "venv", "node_modules", "target"}

    for current_root, dirs, files in os.walk(root):
        rel = Path(current_root).relative_to(root)
        depth = len(rel.parts)
        if depth > max_depth:
            dirs[:] = []
            continue

        dirs[:] = [
            d for d in dirs if d not in skip_dirs and not d.startswith(".")
        ]

        if "yark.json" in files:
            rel_path = "." if rel == Path(".") else rel.as_posix()
            discovered.append(rel_path)
            if len(discovered) >= max_results:
                break

    discovered.sort()
    return discovered


@routes.route("/", methods=["POST", "GET"])
def index():
    """Open channel for non-selected channel"""
    # Redirect to requested channel
    if request.method == "POST":
        name = request.form["channel"]
        return redirect(url_for("routes.channel", name=name, kind="videos"))

    # Show page
    elif request.method == "GET":
        visited = request.cookies.get("visited")
        if visited is not None:
            visited = json.loads(visited)
        discovered = _discover_archives(Path.cwd())
        error = request.args["error"] if "error" in request.args else None
        return render_template(
            "index.html", error=error, visited=visited, discovered=discovered
        )


@routes.route("/channel/<path:name>")
def channel_empty(name):
    """Empty channel url, just redirect to videos by default"""
    return redirect(url_for("routes.channel", name=name, kind="videos"))


@routes.route("/channel/<path:name>/<kind>")
def channel(name, kind):
    """Channel information"""
    if kind not in ["videos", "livestreams", "shorts"]:
        return redirect(url_for("routes.index", error="Video kind not recognised"))

    try:
        channel = Channel.load(name)
        ldir = os.listdir(channel.path / "videos")
        return render_template(
            "channel.html", title=name, channel=channel, name=name, ldir=ldir
        )
    except ArchiveNotFoundException:
        return redirect(
            url_for("routes.index", error="Couldn't open channel's archive")
        )
    except Exception as e:
        return redirect(url_for("routes.index", error=f"Internal server error:\n{e}"))


@routes.route(
    "/channel/<path:name>/<kind>/<id>", methods=["GET", "POST", "PATCH", "DELETE"]
)
def video(name, kind, id):
    """Detailed video information and viewer"""
    if kind not in ["videos", "livestreams", "shorts"]:
        return redirect(
            url_for("routes.channel", name=name, error="Video kind not recognised")
        )

    try:
        # Get information
        channel = Channel.load(name)
        video = channel.search(id)

        # Return video webpage
        if request.method == "GET":
            title = f"{video.title.current()} · {name}"
            views_data = json.dumps(video.views._to_dict())
            likes_data = json.dumps(video.likes._to_dict())
            downloaded = video.downloaded()
            video_file = video.filename()
            return render_template(
                "video.html",
                title=title,
                name=name,
                video=video,
                views_data=views_data,
                likes_data=likes_data,
                downloaded=downloaded,
                video_file=video_file,
            )

        # Add new note
        elif request.method == "POST":
            # Parse json
            new = request.get_json()
            if not "title" in new:
                return "Invalid schema", 400

            # Create note
            timestamp = _decode_timestamp(new["timestamp"])
            title = new["title"]
            body = new["body"] if "body" in new else None
            note = Note.new(video, timestamp, title, body)

            # Save new note
            video.notes.append(note)
            video.channel.commit()

            # Return
            return note._to_dict(), 200

        # Update existing note
        elif request.method == "PATCH":
            # Parse json
            update = request.get_json()
            if not "id" in update or (not "title" in update and not "body" in update):
                return "Invalid schema", 400

            # Find note
            try:
                note = video.search(update["id"])
            except NoteNotFoundException:
                return "Note not found", 404

            # Update and save
            if "title" in update:
                note.title = update["title"]
            if "body" in update:
                note.body = update["body"]
            video.channel.commit()

            # Return
            return "Updated", 200

        # Delete existing note
        elif request.method == "DELETE":
            # Parse json
            delete = request.get_json()
            if not "id" in delete:
                return "Invalid schema", 400

            # Filter out note with id and save
            filtered_notes = []
            for note in video.notes:
                if note.id != delete["id"]:
                    filtered_notes.append(note)
            video.notes = filtered_notes
            video.channel.commit()

            # Return
            return "Deleted", 200

    # Archive not found
    except ArchiveNotFoundException:
        return redirect(
            url_for("routes.index", error="Couldn't open channel's archive")
        )

    # Video not found
    except VideoNotFoundException:
        return redirect(url_for("routes.index", error="Couldn't find video in archive"))

    # Timestamp for note was invalid
    except TimestampException:
        return "Invalid timestamp", 400

    # Unknown error
    except Exception as e:
        return redirect(url_for("routes.index", error=f"Internal server error:\n{e}"))


@routes.route("/archive/<path:name>/video/<file>")
def archive_video(name, file):
    """Serves video file using it's filename (id + ext)"""
    return send_from_directory(os.getcwd(), f"{name}/videos/{file}")


@routes.route("/archive/<path:name>/thumbnail/<id>")
def archive_thumbnail(name, id):
    """Serves thumbnail file using it's id"""
    return send_from_directory(os.getcwd(), f"{name}/thumbnails/{id}.webp")