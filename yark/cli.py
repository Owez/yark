"""Homegrown cli for managing archives"""

from pathlib import Path
from colorama import Style, Fore
import sys
import os
import threading
import webbrowser
from .errors import ArchiveNotFoundException
from .utils import _log_err
from .archiver.archive import Archive
from .archiver.config import Config, DownloadLogger
from .viewer import viewer
import requests
from .utils import PYPI_VERSION
from typing import Optional, Any
from requests.exceptions import HTTPError
from progress.spinner import PieSpinner  # type: ignore
from progress.counter import Pie  # type: ignore
import time
from concurrent.futures import Future, ThreadPoolExecutor

HELP = f"yark [options]\n\n  YouTube archiving made simple.\n\nOptions:\n  new [name] [url]         Creates new archive with name and target url\n  refresh [name] [args?]   Refreshes/downloads archive with optional config\n  view [name?]             Launches offline archive viewer website\n  report [name]            Provides a report on the most interesting changes\n\nExample:\n  $ yark new foobar https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA\n  $ yark refresh foobar\n  $ yark view foobar"
"""User-facing help message provided from the cli"""

download_progress_percentage: float = 0.0
"""Percentage of the current video being downloaded from `DownloadProgressLogger` for use in progress reporting"""


class DownloadProgressLogger(DownloadLogger):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def downloading(d: dict[str, Any]) -> None:
        """Progress hook for video downloading, ignored"""
        if "_percent_str" in d:
            global download_progress_percentage
            download_progress_percentage = float(d["_percent_str"][:-1])


def _cli() -> None:
    """Command-line-interface launcher"""

    # Get arguments
    args = sys.argv[1:]

    # No arguments
    if len(args) == 0:
        print(HELP, file=sys.stderr)
        _log_err(f"\nError: No arguments provided")
        sys.exit(1)

    # Version announcements before going further
    _pypi_version()

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
            _log_err("Please provide an archive name and the target's url")
            sys.exit(1)

        # Create archive
        print(f"Creating new {args[0]} archive..")
        archive = Archive(Path(args[1]), args[2])

        # Commit archive
        archive.commit()

    # Refresh
    elif args[0] == "refresh":
        # More help
        if len(args) == 2 and args[1] == "--help":
            print(
                "yark refresh [name] [args?]\n\n  Refreshes/downloads archive with optional configuration.\n  If a maximum is set, unset categories won't be downloaded\n\nArguments:\n  --comments            Archives all comments (slow)\n  --videos=[max]        Maximum recent videos to download\n  --shorts=[max]        Maximum recent shorts to download\n  --livestreams=[max]   Maximum recent livestreams to download\n\nAdvanced Arguments:\n  --skip-metadata       Skips downloading metadata\n  --skip-download       Skips downloading content\n  --format=[str]        Downloads using custom yt-dlp format\n  --proxy=[str]         Downloads using a proxy server for yt-dlp\n\n Example:\n  $ yark refresh demo\n  $ yark refresh demo --comments\n  $ yark refresh demo --videos=50 --livestreams=2\n  $ yark refresh demo --skip-download"
            )
            sys.exit(0)

        # Bad arguments
        if len(args) < 2:
            _log_err("Please provide the archive name")
            sys.exit(1)

        # Figure out configuration
        config = Config()
        config.hook_logger = DownloadProgressLogger
        config.hook_download = DownloadProgressLogger.downloading
        if len(args) > 2:

            def parse_value(config_arg: str) -> str:
                return config_arg.split("=", 1)[1]

            def parse_maximum_int(config_arg: str) -> int:
                """Tries to parse a maximum integer input"""
                maximum = parse_value(config_arg)
                try:
                    return int(maximum)
                except Exception:
                    print(HELP, file=sys.stderr)
                    _log_err(
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

                elif config_arg.startswith("--cookies="):
                    config.cookies = parse_value(config_arg)

                # Unknown argument
                else:
                    print(HELP, file=sys.stderr)
                    _log_err(
                        f"\nError: Unknown configuration '{config_arg}' provided for archive refresh"
                    )
                    sys.exit(1)

        # Submit config settings
        config.submit()

        # Refresh archive using config context
        try:
            # Load up the archive
            archive = Archive.load(Path(args[1]))

            # Get metadata if wanted
            if config.skip_metadata:
                print("Skipping metadata download..")
            else:
                with ThreadPoolExecutor(1) as executor:
                    # Download raw metadata
                    future_download_metadata = executor.submit(
                        archive.metadata_download, config
                    )
                    _progress_spinner(
                        "Downloading metadata..", future_download_metadata
                    )
                    raw_metadata = future_download_metadata.result()

                    # Parse raw metadata
                    future_parse_metadata = executor.submit(
                        archive.metadata_parse, config, raw_metadata
                    )
                    _progress_spinner("Parsing metadata..", future_parse_metadata)

                    # Commit archive to file
                    archive.commit(True)

            # Download videos if wanted
            if config.skip_download:
                print("Skipping videos/livestreams/shorts download..")
            else:
                with ThreadPoolExecutor(1) as executor:
                    # Download
                    future_download = executor.submit(archive.download, config)
                    _download_progress(future_download)
                    anything_downloaded = future_download.result()

                    # Save if anything was downloaded
                    if anything_downloaded:
                        archive.commit()

            # Report the changes which have been made
            archive.reporter.print()
        except ArchiveNotFoundException:
            _err_archive_not_found()

    # View
    elif args[0] == "view":
        archive_name: Optional[str]
        archive_name = None

        def launch(config: Config, archive_name: Optional[str]) -> None:
            """Launches viewer"""
            url = config.browser_url(archive_name)
            msg = f"Starting archive at {url} address"
            if archive_name is not None:
                msg += f" for {archive_name} archive"

            print(msg)

            app = viewer()
            threading.Thread(target=lambda: app.run(port=config.bind_port, host=config.bind_host)).run()

        # More help
        if len(args) == 2 and args[1] == "--help":
            print(
                f"yark view [name] [args?]\n\n  Launches offline archive viewer website, optionally opening a webbrowser\n  to view a specific archive.\n\nArguments:\n  --headless            Disabled the automatic opening of a web browser\n  --host=[host/ip]      Bind to specific IP or hostname\n  --port=[port number]  Bind to a different port number than the default 7667\n\n Example:\n  $ yark view\n  $ yark view demo\n  $ yark view demo --headless --host=0.0.0.0 --port=8080"
            )
            sys.exit(0)

        # Figure out configuration
        config = Config()
        if len(args) > 1:

            def parse_value(config_arg: str) -> str:
                return config_arg.split("=")[1]

            def parse_port_int(config_arg: str) -> int:
                """Tries to parse a port number input"""
                port = parse_value(config_arg)
                try:
                    portInt = int(port)
                    if portInt < 1 or portInt > 65535:
                        raise Exception("invalid port number")
                    return portInt
                except Exception:
                    print(HELP, file=sys.stderr)
                    _log_err(
                        f"\nError: The value '{port}' isn't a valid port number"
                    )
                    sys.exit(1)

            # Go through each configuration argument
            for config_idx in range(1, len(args)):
                config_arg = args[config_idx]

                # Custom bind host
                if config_arg.startswith("--host="):
                    config.bind_host = parse_value(config_arg)

                # Custom bind port
                elif config_arg.startswith("--port="):
                    config.bind_port = parse_port_int(config_arg)

                # Disable open in webbrowser behaviour
                elif config_arg.startswith("--headless"):
                    config.headless = True

                # Unknown argument
                else:
                    # If config_idx is 1 (first parameter could be name of archive)
                    if config_idx == 1:
                        archive_name = config_arg

                    # If config_idx is not 1
                    # (not the first parameter, wasn't parsed earlier, must be an invalid parameter)
                    else:
                        print(HELP, file=sys.stderr)
                        _log_err(
                            f"\nError: Unknown configuration '{config_arg}' provided for archive view"
                        )
                        sys.exit(1)

        # Submit config settings
        config.submit()

        # Check if running headless, if not then we open a webbrowser for the user
        if not config.headless:
            # If the archive_name was specified
            if archive_name is not None and not Path(archive_name).exists():
                _log_err(
                    f"\nError: Archive doesn't exist '{archive_name}', please make sure you typed it's name correctly"
                )
                sys.exit(1)

            # Open the webbrowser to the specified archive (or main page if no archive is specified)
            config.open_webbrowser(archive_name)

        # Launch HTTP server and block until finished
        launch(config, archive_name)

    # Report
    elif args[0] == "report":
        # Bad arguments
        if len(args) < 2:
            _log_err("Please provide the archive name")
            sys.exit(1)

        archive = Archive.load(Path(args[1]))
        archive.reporter.interesting_changes()

    # Unknown
    else:
        print(HELP, file=sys.stderr)
        _log_err(f"\nError: Unknown command '{args[0]}' provided!", True)
        sys.exit(1)


def _pypi_version() -> None:
    """Checks if there's a new version of Yark and tells the user if it's significant"""

    def get_data() -> Optional[Any]:
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


def _err_archive_not_found() -> None:
    """Errors out the user if the archive doesn't exist"""
    _log_err("Archive doesn't exist, please make sure you typed it's name correctly!")
    sys.exit(1)


def _err_no_help() -> None:
    """Prints out help message and exits, displaying a 'no additional help' message"""
    print(HELP)
    print("\nThere's no additional help for this command")
    sys.exit(0)


def _progress_spinner(msg: str, future: Future[Any]) -> None:
    """Shows a progress spinner displaying `msg` after 2 seconds until future is finished"""
    # Print loading progress at the starts without loading indicator so theres always a print
    print(msg, end="\r")

    # Start spinning
    with PieSpinner(f"{msg} ") as bar:
        # Don't show bar for 2 seconds but check if future is done
        no_bar_time = time.time() + 2
        while time.time() < no_bar_time:
            if future.done():
                return
            time.sleep(0.25)

        # Show loading spinner
        while not future.done():
            bar.next()
            time.sleep(0.075)


def _download_progress(future: Future[Any]) -> None:
    """Gives user user the downloading videos message with a continually resetting progress indicator"""
    with Pie("Downloading videos.. ") as pie:
        # Update the loading pointer until the download is completely finished
        while not future.done():
            # Get the download percentage from the logger hook
            global download_progress_percentage
            if download_progress_percentage == 100.0:
                download_progress_percentage = 0.0

            # Set the pie to be percent complete and wait
            pie.goto(int(download_progress_percentage))
            time.sleep(0.25)

        # Make the pie black (complete) once finished for clarity
        pie.goto(100)
