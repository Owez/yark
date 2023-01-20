"""Archive reporting system allowing detailed logging of useful information"""

from colorama import Fore, Style
import datetime
from .video.video import Video
from ..utils import _truncate_text
from typing import TYPE_CHECKING, Optional
from .video.video import Videos

if TYPE_CHECKING:
    from .archive import Archive


class Reporter:
    archive: "Archive"
    added: list[Video]
    deleted: list[Video]
    updated: list[tuple[str, Video]]

    def __init__(self, archive: "Archive") -> None:
        self.archive = archive
        self.added = []
        self.deleted = []
        self.updated = []

    def print(self) -> None:
        """Prints coloured report to STDOUT"""
        # Initial message
        print(f"Report for {self.archive}:")

        # Updated
        for kind, video in self.updated:
            colour = (
                Fore.CYAN
                if kind in ["title", "description", "undeleted"]
                else Fore.BLUE
            )
            video_fmt = f"  • {video}".ljust(82)
            kind = f" │ 🔥{kind.capitalize()}"

            print(colour + video_fmt + kind)

        # Added
        for video in self.added:
            print(Fore.GREEN + f"  • {video}")

        # Deleted
        for video in self.deleted:
            print(Fore.RED + f"  • {video}")

        # Nothing
        if not self.added and not self.deleted and not self.updated:
            print(Style.DIM + f"  • Nothing was added or deleted")

        # Watermark
        print(_watermark())

    def add_updated(self, kind: str, video: Video) -> None:
        """Tells reporter that an element has been updated"""
        self.updated.append((kind, video))

    def reset(self) -> None:
        """Resets reporting values for new run"""
        self.added = []
        self.deleted = []
        self.updated = []

    def interesting_changes(self) -> None:
        """Reports on the most interesting changes for the archive linked to this reporter"""

        def fmt_video(kind: str, video: Video) -> str:
            """Formats a video if it's interesting, otherwise returns an empty string"""
            # Skip formatting because it's got nothing of note
            if (
                not video.title.changed()
                and not video.description.changed()
                and not video.deleted.changed()
            ):
                return ""

            # Lambdas for easy buffer addition for next block
            buf: list[str] = []
            maybe_capitalize = lambda word: word.capitalize() if len(buf) == 0 else word
            add_buf = lambda name, change, colour: buf.append(
                colour + maybe_capitalize(name) + f" x{change}" + Fore.RESET
            )  # TODO: move to def

            # Figure out how many changes have happened in each category and format them together
            change_deleted = sum(
                1 for value in video.deleted.inner.values() if value == True
            )
            if change_deleted != 0:
                add_buf("deleted", change_deleted, Fore.RED)
            change_description = len(video.description.inner) - 1
            if change_description != 0:
                add_buf("description", change_description, Fore.CYAN)
            change_title = len(video.title.inner) - 1
            if change_title != 0:
                add_buf("title", change_title, Fore.CYAN)

            # Combine the detected changes together and capitalize
            changes = ", ".join(buf) + Fore.RESET

            # Truncate title, get viewer link, and format all together with viewer link
            title = _truncate_text(video.title.current(), 51).strip()
            url = f"http://127.0.0.1:7667/archive/{video.archive}/{kind}/{video.id}"
            return (
                f"  • {title}\n    {changes}\n    "
                + Style.DIM
                + url
                + Style.RESET_ALL
                + "\n"
            )

        def fmt_category(kind: str, videos: Videos) -> Optional[str]:
            """Returns formatted string for an entire category of `videos` inputted or returns nothing"""
            # Add interesting videos to buffer
            HEADING = f"Interesting {kind}:\n"
            buf = HEADING
            for video in videos.inner.values():
                buf += fmt_video(kind, video)

            # Return depending on if the buf is just the heading
            return None if buf == HEADING else buf[:-1]

        # Tell users whats happening
        print(f"Finding interesting changes in {self.archive}..")

        # Get reports on the three categories
        categories = [
            ("videos", fmt_category("videos", self.archive.videos)),
            ("livestreams", fmt_category("livestreams", self.archive.livestreams)),
            ("shorts", fmt_category("shorts", self.archive.shorts)),
        ]

        # Combine those with nothing of note and print out interesting
        not_of_note: list[str] = []
        for name, buf in categories:
            if buf is None:
                not_of_note.append(name)
            else:
                print(buf)

        # Print out those with nothing of note at the end
        if len(not_of_note) != 0:
            not_of_note_fmt = "/".join(not_of_note)
            print(f"No interesting {not_of_note_fmt} found")

        # Watermark
        print(_watermark())


def _watermark() -> str:
    """Returns a new watermark with a Yark timestamp"""
    date = datetime.datetime.utcnow().isoformat()
    return Style.RESET_ALL + f"Yark – {date}"
