"""Channel reporting system allowing detailed logging of useful information."""

import datetime
from typing import TYPE_CHECKING

from ..terminal import ui
from .utils import _truncate_text
from .video import Element, Video

if TYPE_CHECKING:
    from .channel import Channel


class Reporter:
    channel: "Channel"
    added: list[Video]
    deleted: list[Video]
    updated: list[tuple[str, Element]]

    def __init__(self, channel) -> None:
        self.channel = channel
        self.added = []
        self.deleted = []
        self.updated = []

    def print(self):
        """Prints formatted report to STDOUT."""
        updated = [(kind, str(element.video)) for kind, element in self.updated]
        added = [str(video) for video in self.added]
        deleted = [str(video) for video in self.deleted]
        ui.render_change_report(str(self.channel), updated, added, deleted, _watermark())

    def add_updated(self, kind: str, element: Element):
        """Tells reporter that an element has been updated"""
        self.updated.append((kind, element))

    def reset(self):
        """Resets reporting values for new run"""
        self.added = []
        self.deleted = []
        self.updated = []

    def interesting_changes(self):
        """Reports on the most interesting changes for the channel linked to this reporter."""

        def fmt_video(kind: str, video: Video) -> tuple[str, str, str] | None:
            if (
                not video.title.changed()
                and not video.description.changed()
                and not video.deleted.changed()
            ):
                return None

            changes: list[str] = []
            change_deleted = sum(1 for value in video.deleted.inner.values() if value is True)
            if change_deleted != 0:
                changes.append(f"deleted x{change_deleted}")
            change_description = len(video.description.inner) - 1
            if change_description != 0:
                changes.append(f"description x{change_description}")
            change_title = len(video.title.inner) - 1
            if change_title != 0:
                changes.append(f"title x{change_title}")

            title = _truncate_text(video.title.current(), 51).strip()
            url = f"http://127.0.0.1:7667/channel/{video.channel}/{kind}/{video.id}"
            return (title, ", ".join(changes), url)

        ui.info(f"Finding interesting changes in {self.channel}..")
        categories = [
            ("videos", self.channel.videos),
            ("livestreams", self.channel.livestreams),
            ("shorts", self.channel.shorts),
        ]

        empty: list[str] = []
        for kind, videos in categories:
            rows = [row for row in (fmt_video(kind, video) for video in videos) if row]
            if len(rows) == 0:
                empty.append(kind)
            else:
                ui.render_interesting_section(kind, rows)

        if len(empty) != 0:
            ui.render_empty_interesting(empty)

        ui.plain(f"[dim]{_watermark()}[/dim]")


def _watermark() -> str:
    """Returns a new watermark with a Yark timestamp"""
    date = datetime.datetime.utcnow().isoformat()
    return f"Yark - {date}"