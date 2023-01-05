"""Channel reporting system allowing detailed logging of useful information"""

from colorama import Fore, Style
import datetime
from .video import Video, Element
from .utils import _truncate_text


class Reporter:
    def __init__(self, channel) -> None:
        self.channel = channel
        self.added = []
        self.deleted = []
        self.updated = []

    def print(self):
        """Prints coloured report to STDOUT"""
        # Initial message
        print(f"Report for {self.channel}:")

        # Updated
        for type, element in self.updated:
            colour = (
                Fore.CYAN
                if type in ["title", "description", "undeleted"]
                else Fore.BLUE
            )
            video = f"  • {element.video}".ljust(82)
            type = f" │ 🔥{type.capitalize()}"

            print(colour + video + type)

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

    def add_updated(self, kind: str, element: Element):
        """Tells reporter that an element has been updated"""
        self.updated.append((kind, element))

    def reset(self):
        """Resets reporting values for new run"""
        self.added = []
        self.deleted = []
        self.updated = []

    def interesting_changes(self):
        """Reports on the most interesting changes for the channel linked to this reporter"""

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
            buf = []
            maybe_capitalize = lambda word: word.capitalize() if len(buf) == 0 else word
            add_buf = lambda name, change, colour: buf.append(
                colour + maybe_capitalize(name) + f" x{change}" + Fore.RESET
            )

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
            url = f"http://127.0.0.1:7667/channel/{video.channel}/{kind}/{video.id}"
            return (
                f"  • {title}\n    {changes}\n    "
                + Style.DIM
                + url
                + Style.RESET_ALL
                + "\n"
            )

        def fmt_category(kind: str, videos: list) -> str:
            """Returns formatted string for an entire category of `videos` inputted or returns nothing"""
            # Add interesting videos to buffer
            HEADING = f"Interesting {kind}:\n"
            buf = HEADING
            for video in videos:
                buf += fmt_video(kind, video)

            # Return depending on if the buf is just the heading
            return None if buf == HEADING else buf[:-1]

        # Tell users whats happening
        print(f"Finding interesting changes in {self.channel}..")

        # Get reports on the three categories
        categories = [
            ("videos", fmt_category("videos", self.channel.videos)),
            ("livestreams", fmt_category("livestreams", self.channel.livestreams)),
            ("shorts", fmt_category("shorts", self.channel.shorts)),
        ]

        # Combine those with nothing of note and print out interesting
        not_of_note = []
        for name, buf in categories:
            if buf is None:
                not_of_note.append(name)
            else:
                print(buf)

        # Print out those with nothing of note at the end
        if len(not_of_note) != 0:
            not_of_note = "/".join(not_of_note)
            print(f"No interesting {not_of_note} found")

        # Watermark
        print(_watermark())


def _watermark() -> str:
    """Returns a new watermark with a Yark timestamp"""
    date = datetime.datetime.utcnow().isoformat()
    return Style.RESET_ALL + f"Yark – {date}"
