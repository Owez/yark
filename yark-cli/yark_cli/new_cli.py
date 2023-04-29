# Standard Imports
import sys

# Local Imports
from . import archiver, checker, reporter, ReportCode

# External Imports
import click


@click.group()
def entry():
    if not checker.check_version():
        # TODO: Using sys.exit ideology works but might not be intended, check `click` docs
        #       a bit more extensively about doing group return, this is useful for tests
        sys.exit(ReportCode.VersionMismatch)


@entry.command(help='Create a new Archive')
@click.argument('name', type=str)
@click.argument('url', type=str)
@click.option(
    '--output', '-o', type=click.Path(exists=True, dir_okay=True, readable=True, writable=True),
    help='Directory to output archive into')
def new(name, url, output):
    archiver.new(name, url, output)


@entry.command(help='Refreshes/downloads archive with optional config')
@click.argument('name', type=str)
@click.option('--videos', '-v', is_flag=True, help='Skips downloads of videos')
@click.option('--livestreams', '-l', is_flag=True, help='Skips downloads of videos')
@click.option('--shorts', '-s', is_flag=True, help='Skips downloads of videos')
@click.option('--comments', '-c', is_flag=True, help='Fetches comments')
@click.option(
    '--format', '-f', 'format_', type=click.Choice(['1', '2', '3', '4']),
    help='Specify the archive format'
)
@click.option('--proxy', '-p', type=str, help='Use a given proxy')
@click.option('--skip_downloads', '-d', is_flag=True, help='Skips downloads')
@click.option('--skip_metadata', '-m', is_flag=True, help='Skips metadata fetch')
def refresh(name, videos, livestreams, shorts, comments, format_, proxy, skip_downloads, skip_metadata):
    archiver.refresh(name, videos, livestreams, shorts, comments, format_, proxy, skip_downloads, skip_metadata)


@entry.command(help='Launches offline archive viewer website')
@click.argument('name', type=str)
def view(name):
    # TODO: This option might be dropped due to introduction of the ´yark-pages´ project
    raise NotImplementedError


@entry.command(help='Provides a report on the most interesting changes')
@click.argument('name', type=str)
def report(name):
    if not reporter.report(name):
        sys.exit(ReportCode.FailedReport)


def main():
    entry.main()


if __name__ == '__main__':
    main()

