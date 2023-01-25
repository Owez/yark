"""Logging core for formatting output to users"""

from colorama import Style, Fore
import sys
from typing import Any


class VideoLogger:
    @staticmethod
    def downloading(d: dict[str, Any]) -> None:
        """Progress hook for video downloading"""
        # Get video's id
        id = d["info_dict"]["id"]

        # Downloading percent
        if d["status"] == "downloading":
            percent = d["_percent_str"].strip()
            print(
                Style.DIM
                + f"  • Downloading {id}, at {percent}..                "
                + Style.NORMAL,
                end="\r",
            )

        # Finished a video's download
        elif d["status"] == "finished":
            print(Style.DIM + f"  • Downloaded {id}                " + Style.NORMAL)

    def debug(self, _msg: str) -> None:
        """Debug log messages, ignored"""
        pass

    def info(self, _msg: str) -> None:
        """Info log messages ignored"""
        pass

    def warning(self, _msg: str) -> None:
        """Warning log messages ignored"""
        pass

    def error(self, _msg: str) -> None:
        """Error log messages"""
        pass


def _log_err(msg: str, report_msg: bool = False) -> None:
    """Provides a red-coloured error message to the user in the STDERR pipe"""
    msg = (
        msg
        if not report_msg
        else f"{msg}\nPlease file a bug report if you think this is a problem with Yark!"
    )
    print(Fore.RED + Style.BRIGHT + msg + Style.NORMAL + Fore.RESET, file=sys.stderr)
