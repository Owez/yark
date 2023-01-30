# Standard Imports
from typing import Any

# Local Imports
from yark.yark.utils import PYPI_VERSION, _log_err

# External Imports
import requests
from colorama import Fore, Style
from requests import HTTPError


def check_version_upstream() -> None:
    """Checks if there's a new version of Yark and tells the user if it's significant"""

    def get_data() -> Any | None:
        """Gets JSON data for current version of Yark on PyPI or returns nothing if there was a minor error"""
        # Error message to use if this fails
        MINOR_ERROR = (
            "Couldn't check for a new version of Yark, your connection might be faulty!"
        )

        # Try to get from the PyPI API
        try:
            return requests.get("https://pypi.org/pypi/yark/json", timeout=2).json()

        # General HTTP fault
        except HTTPError:
            _log_err(MINOR_ERROR)
            return None

        # Couldn't connect to PyPI immediately
        except requests.exceptions.ConnectionError:
            _log_err(MINOR_ERROR)
            return None

        # Couldn't connect to PyPI after a while
        except TimeoutError:
            _log_err(MINOR_ERROR)
            _log_err(
                Style.DIM + "This was caused by the request timing out" + Style.NORMAL
            )
            return None

    # Get package data from PyPI
    data = get_data()
    if data is None:
        return

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


