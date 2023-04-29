# Standard Imports
import logging
import sys
import time
from typing import TYPE_CHECKING

# Local Imports
from yark.yark.archiving.config.data import Config, YtDlpSettings
from yark.yark.utils import log_err
from yark.yark.exceptions import MetadataFailException
from yark.yark.archiving.archive.data.archive import RawMetadata

if TYPE_CHECKING:
    from yark.yark.archiving.archive.data import Archive, _skip_video
    from yark.yark.archiving.archive.data.video.data import Video
    from yark.yark.archiving.archiver import Converter


# External Imports
from yt_dlp import YoutubeDL, DownloadError


def metadata_download(url: str, config: Config) -> RawMetadata:
    """Downloads raw metadata for further parsing"""
    logging.info(f"Downloading raw metadata for {url}")

    settings = config.into_metadata_settings()

    # Pull metadata from youtube
    with YoutubeDL(settings, auto_init='no_verbose_header') as ydl:
        for i in range(3):
            try:
                res: RawMetadata = ydl.extract_info(url, download=False)
                return res
            except Exception as exception:
                retrying = i != 2
                download_error("metadata", exception, retrying)

                if retrying:
                    logging.warning(f"Retrying metadata download ({i + 1}/3")

    # Couldn't download after all retries
    raise MetadataFailException()


def download(archive: 'Archive', config: 'Config') -> bool:
    """Downloads all videos which haven't already been downloaded, returning if anything was downloaded"""
    logging.debug(f"Downloading curated videos for {archive}")

    # Prepare; clean out old part files and get settings
    archive._clean_parts()
    settings = config.settings_dl(archive.path)

    # Retry downloading 5 times in total for all videos
    anything_downloaded = True
    for i in range(5):
        # Try to curate a list and download videos on it
        try:
            # Curate list of non-downloaded videos
            not_downloaded = archive._curate(config)

            if len(not_downloaded) == 0:
                anything_downloaded = False
                return False

            # Launch core to download all curated videos
            archive._download_launch(settings, not_downloaded)

            # Stop if we've got them all
            break

        # Report error and retry/stop
        except Exception as exception:
            download_error("videos", exception, i != 4)

    # End by converting any downloaded but unsupported video file formats
    if anything_downloaded:
        converter = Converter(archive.path / "videos")
        converter.run()

    # Say that something was downloaded
    return True


def _download_launch(
        self, settings: YtDlpSettings, not_downloaded: list['Video']
) -> None:
    """Downloads all `not_downloaded` videos passed into it whilst automatically handling private videos,
    this is the core of the downloader"""

    # Continuously try to download after private/deleted videos are found
    # This block gives the downloader all the curated videos and skips/reports deleted
    # videos by filtering their exceptions
    while True:
        # Download from curated list then exit the optimistic loop
        try:
            urls = [video.url() for video in not_downloaded]
            with YoutubeDL(settings) as ydl:
                ydl.download(urls)
            break

        # Special handling for private/deleted videos which are archived, if not we raise again
        except DownloadError as exception:
            new_not_downloaded = self._download_exception_handle(
                not_downloaded, exception
            )
            if new_not_downloaded is not None:
                not_downloaded = new_not_downloaded


def _download_exception_handle(
        self, not_downloaded: list['Video'], exception: DownloadError
) -> list['Video'] | None:
    """Handle for failed downloads if there's a special private/deleted video"""
    # Set new list for not downloaded to return later
    new_not_downloaded = None

    # Video is private or deleted
    if (
            "Private video" in exception.msg
            or "This video has been removed by the uploader" in exception.msg
    ):
        # Skip video from curated and get it as a return
        new_not_downloaded, video = _skip_video(not_downloaded, "deleted")

        # If this is a new occurrence then set it & report
        # This will only happen if it's deleted after getting metadata, like in a dry run
        if not video.deleted.current():
            self.reporter.deleted.append(video)
            video.deleted.update(None, True)

    # User hasn't got ffmpeg installed and YouTube hasn't got format 22
    # NOTE: see #55 <https://github.com/Owez/yark/issues/55> to learn more
    # NOTE: sadly yt-dlp doesn't let us access yt_dlp.utils.ContentTooShortError so we check msg
    elif " bytes, expected " in exception.msg:
        # Skip video from curated
        new_not_downloaded, _ = _skip_video(
            not_downloaded,
            "no format found; please download ffmpeg!",
            True,
        )

    # Never-mind, normal exception
    else:
        raise exception

    return new_not_downloaded


errors: list[str] = [
    "<urlopen error [Errno 8] nodename nor servname provided, or not known>",
    "500",
    "Got error: The read operation timed out",
    "No such file or directory",
    "HTTP Error 404: Not Found",
    "<urlopen error timed out>",
    "Did not get any data blocks",
]

messages: dict[str, str] = {
    errors[0]: "Issue connecting to Youtube's servers",  # Server connection
    errors[1]: "Fault with Youtube's servers",  # Server fault
    errors[2]: "Timed out trying to downloads video",  # Timeout
    errors[3]: "Video deleted whilst downloading",
    errors[4]: "Couldn't find target by Id",  # Target not found, might need to retry with alternative route
    errors[5]: "Timed out trying to reach YouTube"  # Random timeout; not sure if its user-end or youtube-end
}


def download_error(archive_name: str, exception: DownloadError, retrying: bool):
    """Logs errors depending on what kind of download error occurred"""
    # Default message
    msg = (
        f"Unknown error whilst downloading {archive_name}, details below:\n{exception}"
    )

    # Download errors
    if type(exception) == DownloadError:
        def pick() -> str | None:
            for _, m in messages.items():
                if m in exception.msg:
                    return m

            return None

        msg = pick()

    # Log error
    suffix = ", retrying in a few seconds.." if retrying else ""
    logging.warning(msg + suffix)

    # Wait if retrying, exit if failed
    if retrying:
        time.sleep(5)
    else:
        log_err(f"Sorry, failed to download {archive_name}", True)
        sys.exit(1)
