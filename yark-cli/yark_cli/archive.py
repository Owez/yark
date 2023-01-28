# Standard Imports
import sys
from pathlib import Path

# Local Imports

# External Imports
from yark.yark_lib.archiver.archive import Archive
from yark.yark_lib.archiver.config import Config
from yark.yark_lib.errors import ArchiveNotFoundException
from yark.yark_lib.utils import _log_err


def refresh(config: Config, path: Path):
    # TODO: Strip out necessary code from this comment
    """

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

    """

    try:
        archive = Archive.load(path)

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


def _err_archive_not_found() -> None:
    """Errors out the user if the archive doesn't exist"""
    _log_err("Archive doesn't exist, please make sure you typed it's name correctly!")
    sys.exit(1)


# TODO: Strip out necessary code, from the *refresh* function comment
'''
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
'''