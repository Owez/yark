# Standard Imports
import sys
from typing import Optional, Any

# Local Imports

# External Imports
from yark.yark.utils import PYPI_VERSION
from yark.yark.logger import _err_msg

import requests
from colorama import Fore, Style
from requests import HTTPError


def check_version_upstream() -> bool:
    """Checks if there's a new version of Yark and tells the user if it's significant"""

    def get_data() -> Optional[Any]:
        """Gets JSON data for current version of Yark on PyPI or returns nothing if there was a minor error"""
        minor_error = lambda: _err_msg(
            "Couldn't check for a new version of Yark, your connection might be faulty!"
        )

        try:
            return requests.get("https://pypi.org/pypi/yark/json", timeout=2).json()
        except HTTPError or ConnectionError:
            minor_error()
            return False
        except TimeoutError:
            minor_error()
            _err_msg(
                Style.DIM + "This was caused by the request timing out" + Style.NORMAL
            )
            return False

    # Get package data from PyPI
    data = get_data()
    if data is None:
        return False

    # Decode their versioning information
    rewrite_and_major = [int(v) for v in data["info"]["version"].split(".")[:2]]
    their_rewrite, their_major = (rewrite_and_major[0], rewrite_and_major[1])

    # Get our versioning information from local hardcoded constant
    our_rewrite, our_major = PYPI_VERSION

    # Compare versions
    if their_rewrite > our_rewrite or their_major > our_major:
        print(
            Fore.YELLOW
            + "There's a major update for Yark ready to download, please update!"
            + Fore.RESET
        )


def _err_archive_not_found():
    """Errors out the user if the archive doesn't exist"""
    _err_msg("Archive doesn't exist, please make sure you typed it's name correctly!")
    sys.exit(1)


def _err_no_help():
    """Prints out help message and exits, displaying a 'no additional help' message"""
    print(HELP)
    print("\nThere's no additional help for this command")
    sys.exit(0)
