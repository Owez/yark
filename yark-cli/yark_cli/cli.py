# Standard Imports
import argparse
import sys
from pathlib import Path

# Local Imports
import archive

# External Imports
from yark.yark import logger
from yark.yark import archive
from yark.yark import Config
from yark.yark import Archive
from yark.yark import pypi
from yark.yark import err_archive_not_found
from yark.yark.archiver.logger import DownloadProgressLogger

from colorama import Style


def new(args):
    Archive.new(Path(args.name), args.url)


def refresh(args):
    config = Config()
    config.hook_logger = DownloadProgressLogger
    config.hook_download = DownloadProgressLogger.downloading

    config.comments = args.comments
    config.skip_metadata = args.skip_metadata
    config.skip_download = args.skip_download
    config.max_videos = args.videos
    config.max_livestreams = args.livestreams
    config.max_shorts = args.shorts
    config.format = args.format
    config.proxy = args.proxy

    config.submit()

    archive.refresh(config, args[1])


def view(args):
    if args.name:
        path = Path(args.name)

        if not path.exists():
            err_archive_not_found()

        browser.open_with_archive(args.name)
    else:
        browser.open_general()


def report(args):
    report_archive = Archive.load(Path(args.name))
    report_archive.reporter.interesting_changes()


def parse_args(args):
    parser = argparse.ArgumentParser(
        prog="Yark",
        usage="yark",
        description='Yark CLI - YouTube archiving made simple',
        epilog="Example: yark new foobar https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA"
    )
    subparsers = parser.add_subparsers()

    # New option parser
    new_parser = subparsers.add_parser(
        'new', help='Creates new archive with name and target url'
    )
    new_parser.add_argument('name', type=str)
    new_parser.add_argument('url', type=str)
    new_parser.set_defaults(func=new)

    # Refresh option parser
    refresh_parser = subparsers.add_parser('refresh', help="Refreshes/downloads archive with optional config")
    refresh_parser.add_argument('name', type=str)

    refresh_parser.add_argument('--videos', type=bool, default=False, help='Skips downloads of videos')
    refresh_parser.add_argument('--livestreams', type=bool, default=False)
    refresh_parser.add_argument('--shorts', type=bool, default=False)
    refresh_parser.add_argument('--format', type=str)
    refresh_parser.add_argument('--proxy', type=str)
    refresh_parser.add_argument('--comments', type=bool, default=False)
    refresh_parser.add_argument('--skip-downloads', type=bool, default=False, help='Skips downloads of videos')
    refresh_parser.add_argument('--skip_metadata', type=bool, default=False)
    refresh_parser.set_defaults(func=refresh)

    # View option parser
    view_parser = subparsers.add_parser('view', help='Launches offline archive viewer website')
    view_parser.add_argument('name', type=str, default=None, help='')
    view_parser.set_defaults(func=view)

    # Report option parser
    report_parser = subparsers.add_parser('report', help='Provides a report on the most interesting changes')
    report_parser.add_argument('name', type=str, default=None)
    report_parser.set_defaults(func=report)

    return parser.parse_args(args)


def entry(args):
    # Version announcements before going further
    try:
        pypi.check_version_upstream()
    except Exception as err:
        logger.err_msg(
            f"Error: Failed to check for new Yark version, info:\n"
            + Style.NORMAL
            + str(err)
            + Style.BRIGHT,
            True,
        )

    # Parse CLI args and take actions
    args = parse_args(args)
    args.func(args)


if __name__ == '__main__':
    entry(sys.argv[1:])
    # entry(['-h'])
