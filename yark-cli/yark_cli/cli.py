# Standard Imports
import argparse
import sys
from pathlib import Path

# Local Imports
from . import archiver, reporter, viewer, checker

# External Imports
from yark.archiver.archive import Archive


def new(args):
    Archive(Path(args.name), args.url)


def refresh(args):
    archiver.refresh(
        args.name, args.videos, args.livestreams, args.shorts, args.comments,
        args.format_, args.proxy, args.skip_downloads, args.skip_metadata
    )


def view(args):
    viewer.view(args.name)


def report(args):
    reporter.report(args.name)


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
    if not checker.check_version:
        return

    # Parse CLI args and take actions
    args = parse_args(args)
    args.func(args)


def main():
    entry(sys.argv[1:])


if __name__ == '__main__':
    main()

