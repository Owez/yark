"""Homegrown cli for managing archives"""

import json
from pathlib import Path
from colorama import Style, Fore
import sys
import threading
import webbrowser
from importlib.metadata import version
from .errors import ArchiveNotFoundException
from .logger import _err_msg
from .archiver.archive import Archive
from .archiver.config import Config
from .viewer import viewer
import requests
from .utils import PYPI_VERSION
from typing import Optional, Any
from requests.exceptions import HTTPError, ConnectionError

HELP = f"yark [options]\n\n  YouTube archiving made simple.\n\nOptions:\n  new [name] [url]         Creates new archive with name and target url\n  refresh [name] [args?]   Refreshes/downloads archive with optional config\n  view [name?]             Launches offline archive viewer website\n  report [name]            Provides a report on the most interesting changes\n\nExample:\n  $ yark new foobar https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA\n  $ yark refresh foobar\n  $ yark view foobar"
"""User-facing help message provided from the cli"""


def _cli():
    """Command-line-interface launcher"""

    # Get arguments
    args = sys.argv[1:]

    # No arguments
    if len(args) == 0:
        print(HELP, file=sys.stderr)
        _err_msg(f"\nError: No arguments provided")
        sys.exit(1)

    # Version announcements before going further
    try:
        _pypi_version()
    except Exception as err:
        _err_msg(
            f"Error: Failed to check for new Yark version, info:\n"
            + Style.NORMAL
            + str(err)
            + Style.BRIGHT,
            True,
        )

    # Help
    if args[0] in ["help", "--help", "-h"]:
        print(HELP)
        sys.exit(0)

    # Create new
    elif args[0] == "new":
        # More help
        if len(args) == 2 and args[1] == "--help":
            _err_no_help()

        # Bad arguments
        if len(args) < 3:
            _err_msg("Please provide an archive name and the target's url")
            sys.exit(1)

        # Create archive
        Archive.new(Path(args[1]), args[2])

    # Refresh
    elif args[0] == "refresh":
        # More help
        if len(args) == 2 and args[1] == "--help":
            print(
                f"yark refresh [name] [args?]\n\n  Refreshes/downloads archive with optional configuration.\n  If a maximum is set, unset categories won't be downloaded\n\nArguments:\n  --comments            Archives all comments (slow)\n  --videos=[max]        Maximum recent videos to download\n  --shorts=[max]        Maximum recent shorts to download\n  --livestreams=[max]   Maximum recent livestreams to download\n\nAdvanced Arguments:\n  --skip-metadata       Skips downloading metadata\n  --skip-download       Skips downloading content\n  --format=[str]        Downloads using custom yt-dlp format\n  --proxy=[str]         Downloads using a proxy server for yt-dlp\n\n Example:\n  $ yark refresh demo\n  $ yark refresh demo --comments\n  $ yark refresh demo --videos=50 --livestreams=2\n  $ yark refresh demo --skip-download"
            )
            sys.exit(0)

        # Bad arguments
        if len(args) < 2:
            _err_msg("Please provide the archive name")
            sys.exit(1)

        # Figure out configuration
        config = Config()
        if len(args) > 2:

            def parse_value(config_arg: str) -> str:
                return config_arg.split("=")[1]

            def parse_maximum_int(config_arg: str) -> int:
                """Tries to parse a maximum integer input"""
                maximum = parse_value(config_arg)
                try:
                    return int(maximum)
                except:
                    print(HELP, file=sys.stderr)
                    _err_msg(
                        f"\nError: The value '{maximum}' isn't a valid maximum number"
                    )
                    sys.exit(1)

            # Go through each configuration argument
            for config_arg in args[2:]:
                # Enable comment fetching
                if config_arg.startswith("--comments"):
                    config.comments = True

                # Video maximum
                elif config_arg.startswith("--videos="):
                    config.max_videos = parse_maximum_int(config_arg)

                # Livestream maximum
                elif config_arg.startswith("--livestreams="):
                    config.max_livestreams = parse_maximum_int(config_arg)

                # Shorts maximum
                elif config_arg.startswith("--shorts="):
                    config.max_shorts = parse_maximum_int(config_arg)

                # No metadata
                elif config_arg == "--skip-metadata":
                    config.skip_metadata = True

                # No downloading; functionally equivalent to all maximums being 0 but it skips entirely
                elif config_arg == "--skip-download":
                    config.skip_download = True

                # Custom yt-dlp format
                elif config_arg.startswith("--format="):
                    config.format = parse_value(config_arg)

                # Custom yt-dlp proxy
                elif config_arg.startswith("--proxy="):
                    config.proxy = parse_value(config_arg)

                # Unknown argument
                else:
                    print(HELP, file=sys.stderr)
                    _err_msg(
                        f"\nError: Unknown configuration '{config_arg}' provided for archive refresh"
                    )
                    sys.exit(1)

        # Submit config settings
        config.submit()

        # Refresh archive using config context
        try:
            archive = Archive.load(Path(args[1]))
            if config.skip_metadata:
                print("Skipping metadata download..")
            else:
                archive.metadata(config)
                archive.commit(True)
            if config.skip_download:
                print("Skipping videos/livestreams/shorts download..")
            else:
                archive.download(config)
                archive.commit()
            archive.reporter.print()
        except ArchiveNotFoundException:
            _err_archive_not_found()

    # View
    elif args[0] == "view":

        def launch():
            """Launches viewer"""
            app = viewer()
            threading.Thread(target=lambda: app.run(port=7667)).run()

        # More help
        if len(args) == 2 and args[1] == "--help":
            _err_no_help()

        # Start on archive name
        if len(args) > 1:
            # Get name
            archive_name = args[1]

            # Jank archive check
            if not Path(archive_name).exists():
                _err_archive_not_found()

            # Launch and start browser
            print(f"Starting viewer for {archive_name}..")
            webbrowser.open(f"http://127.0.0.1:7667/archive/{archive_name}/videos")
            launch()

        # Start on archive finder
        else:
            print("Starting viewer..")
            webbrowser.open(f"http://127.0.0.1:7667/")
            launch()

    # Report
    elif args[0] == "report":
        # Bad arguments
        if len(args) < 2:
            _err_msg("Please provide the archive name")
            sys.exit(1)

        archive = Archive.load(Path(args[1]))
        archive.reporter.interesting_changes()

    # Unknown
    else:
        print(HELP, file=sys.stderr)
        _err_msg(f"\nError: Unknown command '{args[0]}' provided!", True)
        sys.exit(1)


def _pypi_version():
    """Checks if there's a new version of Yark and tells the user if it's significant"""

    def get_data() -> Optional[Any]:
        """Gets JSON data for current version of Yark on PyPI or returns nothing if there was a minor error"""
        minor_error = lambda: _err_msg(
            "Couldn't check for a new version of Yark, your connection might be faulty!"
        )
        try:
            return requests.get("https://pypi.org/pypi/yark/json", timeout=2).json()
        except HTTPError:
            minor_error()
            return None
        except ConnectionError:
            minor_error()
            return None
        except TimeoutError:
            minor_error()
            _err_msg(
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


def _err_archive_not_found():
    """Errors out the user if the archive doesn't exist"""
    _err_msg("Archive doesn't exist, please make sure you typed it's name correctly!")
    sys.exit(1)


def _err_no_help():
    """Prints out help message and exits, displaying a 'no additional help' message"""
    print(HELP)
    print("\nThere's no additional help for this command")
    sys.exit(0)
