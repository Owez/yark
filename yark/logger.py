"""Logging core for formatting output to users"""

from colorama import Style, Fore
import sys


class VideoLogger:
    @staticmethod
    def downloading(d):
        """Progress hook for video downloading"""
        # Get video's id
        id = d["info_dict"]["id"]

        # Downloading percent
        if d["status"] == "downloading":
            percent = d["_percent_str"].strip()
            print(
                Style.DIM + f"  • Downloading {id}, at {percent}.." + Style.NORMAL,
                end="\r",
            )

        # Finished a video's download
        elif d["status"] == "finished":
            print(
                Style.DIM
                + f"  • Downloaded {id}                               "
                + Style.NORMAL
            )

    def debug(self, msg):
        """Debug log messages, ignored"""
        pass

    def info(self, msg):
        """Info log messages ignored"""
        pass

    def warning(self, msg):
        """Warning log messages ignored"""
        pass

    def error(self, msg):
        """Error log messages"""
        pass


def _err_msg(msg: str, report_msg: bool = False):
    """Provides a red-coloured error message to the user in the STDERR pipe"""
    msg = (
        msg
        if not report_msg
        else f"{msg}\nPlease file a bug report if you think this is a problem with Yark!"
    )
    print(Fore.RED + Style.BRIGHT + msg + Style.NORMAL + Fore.RESET, file=sys.stderr)
