from flask import (
    Flask,
    redirect,
    render_template,
    request,
    url_for,
    send_from_directory,
)
import json
import logging
import os

# TODO: restructure this
def viewer() -> Flask:
    """Generates viewer flask app, launch by just using the typical `app.run()`"""
    # Make flask app
    app = Flask(__name__)

    # Only log errors
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    # Routing
    @app.route("/", methods=["POST", "GET"])
    def index():
        """Open channel for non-selected channel"""
        # Redirect to requested channel
        if request.method == "POST":
            name = request.form["channel"]
            return redirect(url_for("channel", name=name, kind="videos"))

        # Show page
        elif request.method == "GET":
            visited = request.cookies.get("visited")
            if visited is not None:
                visited = json.loads(visited)
            error = request.args["error"] if "error" in request.args else None
            return render_template("index.html", error=error, visited=visited)

    @app.route("/channel/<name>")
    def channel_empty(name):
        """Empty channel url, just redirect to videos by default"""
        return redirect(url_for("channel", name=name, kind="videos"))

    @app.route("/channel/<name>/<kind>")
    def channel(name, kind):
        """Channel information"""
        if kind not in ["videos", "livestreams", "shorts"]:
            return redirect(url_for("index", error="Video kind not recognised"))

        try:
            channel = Channel.load(name)
            ldir = os.listdir(channel.path / "videos")
            return render_template(
                "channel.html", title=name, channel=channel, name=name, ldir=ldir
            )
        except ArchiveNotFoundException:
            return redirect(url_for("index", error="Couldn't open channel's archive"))
        except Exception as e:
            return redirect(url_for("index", error=f"Internal server error:\n{e}"))

    @app.route(
        "/channel/<name>/<kind>/<id>", methods=["GET", "POST", "PATCH", "DELETE"]
    )
    def video(name, kind, id):
        """Detailed video information and viewer"""
        if kind not in ["videos", "livestreams", "shorts"]:
            return redirect(
                url_for("channel", name=name, error="Video kind not recognised")
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
                return render_template(
                    "video.html",
                    title=title,
                    video=video,
                    views_data=views_data,
                    likes_data=likes_data,
                )

            # Add new note
            elif request.method == "POST":
                # Parse json
                new = request.get_json()
                if not "title" in new:
                    return "Invalid schema", 400

                # Create note
                timestamp = _parse_timestamp(new["timestamp"])
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
                if not "id" in update or (
                    not "title" in update and not "body" in update
                ):
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
            return redirect(url_for("index", error="Couldn't open channel's archive"))

        # Video not found
        except VideoNotFoundException:
            return redirect(url_for("index", error="Couldn't find video in archive"))

        # Timestamp for note was invalid
        except TimestampException:
            return "Invalid timestamp", 400

        # Unknown error
        except Exception as e:
            return redirect(url_for("index", error=f"Internal server error:\n{e}"))

    @app.route("/archive/<path:target>")
    def archive(target):
        """Serves archive files"""
        return send_from_directory(os.getcwd(), target)

    @app.template_filter("timestamp")
    def _jinja2_filter_timestamp(timestamp, fmt=None):
        """Formatter hook for timestamps"""
        return _fmt_timestamp(timestamp)

    return app


def _parse_timestamp(input: str) -> int:
    """Parses timestamp into seconds or raises `TimestampException`"""
    # Check existence
    input = input.strip()
    if input == "":
        raise TimestampException("No input provided")

    # Split colons
    splitted = input.split(":")
    splitted.reverse()
    if len(splitted) > 3:
        raise TimestampException("Days and onwards aren't supported")

    # Parse
    secs = 0
    try:
        # Seconds
        secs += int(splitted[0])

        # Minutes
        if len(splitted) > 1:
            secs += int(splitted[1]) * 60

        # Hours
        if len(splitted) > 2:
            secs += int(splitted[2]) * 60 * 60
    except:
        raise TimestampException("Only numbers are allowed in timestamps")

    # Return
    return secs


def _fmt_timestamp(timestamp: int) -> str:
    """Formats previously parsed human timestamp for notes, e.g. `02:25`"""
    # Collector
    parts = []

    # Hours
    if timestamp >= 60 * 60:
        # Get hours float then append truncated
        hours = timestamp / (60 * 60)
        parts.append(str(int(hours)).rjust(2, "0"))

        # Remove truncated hours from timestamp
        timestamp = int((hours - int(hours)) * 60 * 60)

    # Minutes
    if timestamp >= 60:
        # Get minutes float then append truncated
        minutes = timestamp / 60
        parts.append(str(int(minutes)).rjust(2, "0"))

        # Remove truncated minutes from timestamp
        timestamp = int((minutes - int(minutes)) * 60)

    # Seconds
    if len(parts) == 0:
        parts.append("00")
    parts.append(str(timestamp).rjust(2, "0"))

    # Return
    return ":".join(parts)
