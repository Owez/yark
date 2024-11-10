"""Homegrown cli for managing archives"""

from pathlib import Path
from colorama import Style, Fore
import sys
import threading
import webbrowser
from .errors import _err_msg, ArchiveNotFoundException
from .channel import Channel, DownloadConfig
from .viewer import viewer

HELP = f"yark [options]\n\n  YouTube archiving made simple.\n\nOptions:\n  new [name] [url]         Creates new archive with name and channel url\n  refresh [name] [args?]   Refreshes/downloads archive with optional config\n  view [name?]             Launches offline archive viewer website\n  report [name]            Provides a report on the most interesting changes\n\nExample:\n  $ yark new owez https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA\n  $ yark refresh owez\n  $ yark view owez"
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

    # Help
    if args[0] in ["help", "--help", "-h"]:
        print(HELP)

    # Version
    # TODO: automatically track this
    elif args[0] in ["-v", "-ver", "--version", "--v"]:
        print("1.2.9")

    # Create new
    elif args[0] == "new":
        # More help
        if len(args) == 2 and args[1] == "--help":
            _err_no_help()

        # Bad arguments
        if len(args) < 3:
            _err_msg("Please provide an archive name and the channel url")
            sys.exit(1)

        # Create channel
        Channel.new(Path(args[1]), args[2])

    # Refresh
    elif args[0] == "refresh":
        # More help
        if len(args) == 2 and args[1] == "--help":
            # NOTE: if these get more complex, separate into something like "basic config" and "advanced config"
            print(
                f"yark refresh [name] [args?]\n\n  Refreshes/downloads archive with optional configuration.\n  If a maximum is set, unset categories won't be downloaded\n\nArguments:\n  --videos=[max]        Maximum recent videos to download\n  --shorts=[max]        Maximum recent shorts to download\n  --livestreams=[max]   Maximum recent livestreams to download\n  --skip-metadata       Skips downloading metadata\n  --skip-download       Skips downloading content\n  --format=[str]        Downloads using custom yt-dlp format for advanced users\n\n Example:\n  $ yark refresh demo\n  $ yark refresh demo --videos=5\n  $ yark refresh demo --shorts=2 --livestreams=25\n  $ yark refresh demo --skip-download"
            )
            sys.exit(0)

        # Bad arguments
        if len(args) < 2:
            _err_msg("Please provide the archive name")
            sys.exit(1)

        # Figure out configuration
        config = DownloadConfig()
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
                # Video maximum
                if config_arg.startswith("--videos="):
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

                # Unknown argument
                else:
                    print(HELP, file=sys.stderr)
                    _err_msg(
                        f"\nError: Unknown configuration '{config_arg}' provided for archive refresh"
                    )
                    sys.exit(1)

        # Submit config settings
        config.submit()

        # Refresh channel using config context
        try:
            channel = Channel.load(args[1])
            if config.skip_metadata:
                print("Skipping metadata download..")
            else:
                channel.metadata()
                channel.commit()  # NOTE: Do it here no matter, because it's metadata. Downloads do not modify the archive
            if config.skip_download:
                print("Skipping videos/livestreams/shorts download..")
            else:
                channel.download(config)
            channel.reporter.print()
        except ArchiveNotFoundException:
            _err_archive_not_found()

    # View
    elif args[0] == "view":
        # More help
        if len(args) == 2 and args[1] == "--help":
            print(
                f"yark view [name] [args?]\n\n  Launches offline archive viewer website.\n\nArguments:\n  --host [str] Custom uri to act as host from\n  --port [int] Custom port number instead of 7667\n\n Example:\n  $ yark view foobar\n  $ yark view foobar --port=80\n  $ yark view foobar --port=1234 --host=0.0.0.0"
            )
            sys.exit(0)

        # Basis for custom host/port configs
        host = None
        port = 7667

        # Go through each configuration argument
        for config_arg in args[2:]:
            # Host configuration
            if config_arg.startswith("--host="):
                host = config_arg[7:]

            # Port configuration
            elif config_arg.startswith("--port="):
                if config_arg[7:].strip() == "":
                    print(
                        f"No port number provided for port argument",
                        file=sys.stderr,
                    )
                    sys.exit(1)
                try:
                    port = int(config_arg[7:])
                except:
                    print(
                        f"Invalid port number '{config_arg[7:]}' provided",
                        file=sys.stderr,
                    )
                    sys.exit(1)

        def launch():
            """Launches viewer"""
            app = viewer()
            threading.Thread(target=lambda: app.run(host=host, port=port)).run()

        # Start on channel name
        if len(args) > 1:
            # Get name
            channel = args[1]

            # Jank archive check
            if not Path(channel).exists():
                _err_archive_not_found()

            # Launch and start browser
            print(f"Starting viewer for {channel}..")
            webbrowser.open(f"http://127.0.0.1:7667/channel/{channel}/videos")
            launch()

        # Start on channel finder
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

        channel = Channel.load(Path(args[1]))
        channel.reporter.interesting_changes()

    # Unknown
    else:
        print(HELP, file=sys.stderr)
        _err_msg(f"\nError: Unknown command '{args[0]}' provided!", True)
        sys.exit(1)


def _err_archive_not_found():
    """Errors out the user if the archive doesn't exist"""
    _err_msg("Archive doesn't exist, please make sure you typed it's name correctly!")
    sys.exit(1)


def _err_no_help():
    """Prints out help message and exits, displaying a 'no additional help' message"""
    print(HELP)
    print("\nThere's no additional help for this command")
    sys.exit(0)


# NOTE: not used, not sure why this is included. might be useful for the future
# def _upgrade_messaging() -> None:
#     """
#     Give users some info on the new Yark 1.3 version because because PyPI releases aren't supported

#     This wouldn't happen normally but users might be confused seeing as we're switching distribution methods.
#     """
#     # Major update message for 1.3
#     print(
#         Style.BRIGHT
#         + "Yark 1.3 is out now! Go to https://github.com/Owez/yark to download"
#         + Style.DIM
#         + " (pip is no longer supported)"
#         + Style.NORMAL
#     )

#     # Give a warning if it's been over a year since release
#     if datetime.datetime.utcnow().year >= 2024:
#         print(
#             Fore.YELLOW
#             + "You're currently on an outdated version of Yark"
#             + Fore.RESET,
#             file=sys.stderr,
#         )
