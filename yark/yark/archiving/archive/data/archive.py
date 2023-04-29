"""Archive management with metadata/video downloading core"""
# Standard Imports
from __future__ import annotations
from typing import Optional, Any, NewType
from dataclasses import dataclass
from pathlib import Path
import logging
import json

# Local Imports
from yark.yark.archiving.archive.data.comment_author import CommentAuthor
from yark.yark.archiving.archiver.reporter import Reporter
from yark.yark.archiving.config.data import Config
from yark.yark.archiving.archive.data.video.data import Video
from yark.yark.archiving.archive.data.video.videos import Videos
from yark.yark.utils import ARCHIVE_SCHEMA_COMPAT
from yark.yark import utils

# External Imports
from yt_dlp import YoutubeDL, DownloadError  # type: ignore  # noqa


RawMetadata = NewType("RawMetadata", dict[str, Any])
"""Raw metadata downloaded from yt-dlp to be parsed"""


@dataclass(init=False)
class Archive:

    version: int
    videos: Videos
    livestreams: Videos
    shorts: Videos
    reporter: Reporter
    comment_authors: dict[str, CommentAuthor]

    def __init__(
        self,
        path: Path,
        url: str,
        version: int = ARCHIVE_SCHEMA_COMPAT,
        videos: Videos | None = None,
        livestreams: Videos | None = None,
        shorts: Videos | None = None,
        comment_authors: dict[str, CommentAuthor] | None = None,
    ) -> None:
        if comment_authors is None:
            comment_authors = {}

        self.path = path
        self.url = url
        self.version = version
        self.videos = Videos(self) if videos is None else videos
        self.livestreams = Videos(self) if livestreams is None else livestreams
        self.shorts = Videos(self) if shorts is None else shorts
        self.reporter = Reporter(self)
        self.comment_authors = comment_authors

    """
    def __post_init__(self):
        if not self.videos: 
            self.videos = Videos(self)
    """

    def metadata_parse(self, config: Config, metadata: RawMetadata) -> None:
        """Updates current archive by parsing the raw downloaded metadata"""
        logging.info(f"Parsing downloaded metadata for {self}")

        # Make buckets to normalize different types of videos
        videos = []
        livestreams = []
        shorts = []

        # Videos only (basic channel or playlist)
        if "entries" not in metadata["entries"][0]:
            videos = metadata["entries"]

        # Videos and at least one other (livestream/shorts)
        else:
            for entry in metadata["entries"]:
                # Find the kind of category this is; YouTube formats these as 3 playlists
                kind = entry["title"].split(" - ")[-1].lower()

                match kind:
                    case 'videos':
                        videos = entry['entries']
                    case 'live':
                        livestreams = entry['entries']
                    case 'shorts':
                        shorts = entry['entries']
                    case _:
                        # Unknown nth kind; YouTube might've updated
                        utils.log_err(f"Unknown video kind '{kind}' found", True)

        # Parse metadata
        self._metadata_parse_videos("video", config, videos, self.videos)
        self._metadata_parse_videos("livestream", config, livestreams, self.livestreams)
        self._metadata_parse_videos("shorts", config, shorts, self.shorts)

        # Go through each and report deleted
        self._report_deleted(self.videos)
        self._report_deleted(self.livestreams)
        self._report_deleted(self.shorts)

    def _metadata_parse_videos(
        self,
        kind: str,
        config: Config,
        entries: list[dict[str, Any]],
        videos: Videos,
    ) -> None:
        """Parses metadata for a category of video into it's `videos` bucket"""
        logging.debug(f"Parsing through {kind} for {self}")

        # Parse each video
        for entry in entries:
            self._metadata_parse_video(config, entry, videos)

        # Sort videos by newest
        videos.sort()

    def _metadata_parse_video(
        self, config: Config, entry: dict[str, Any], videos: Videos
    ) -> None:
        """Parses metadata for one video, creating it or updating it depending on the `videos` already in the bucket"""
        kind = entry["id"]
        logging.debug(f"Parsing video {kind} metadata for {self}")

        # Skip video if there's no formats available; happens with upcoming videos/livestreams
        if "formats" not in entry or len(entry["formats"]) == 0:
            return

        # Updated intra-loop marker
        updated = False

        # Update video if it exists
        found_video = videos.inner.get(entry["id"])
        if found_video is not None:
            found_video.update(config, entry)
            updated = True
            return

        # Add new video if not
        if not updated:
            video = Video(config, self, entry)
            videos.inner[video.id] = video
            self.reporter.added.append(video)

    def _curate(self, config: Config) -> list[Video]:
        """Curate videos which aren't downloaded and return their urls"""

        def curate_list(videos: Videos, maximum: Optional[int]) -> list[Video]:
            """Curates the videos inside the provided `videos` list to its local maximum"""

            found_videos = []

            # Add all un-downloaded videos because there's no maximum
            if maximum is None:
                found_videos = list(
                    [video for video in videos.inner.values() if not video.downloaded()]
                )

            # Cut available videos to maximum if present for deterministic getting
            else:
                # Fix the maximum to the length, so we don't try to get more than there is
                fixed_maximum = min(max(len(videos.inner) - 1, 0), maximum)

                # Set the available videos to this fixed maximum
                values = list(videos.inner.values())
                for ind in range(fixed_maximum):
                    video = values[ind]

                    # Save video if it's not been downloaded yet
                    if not video.downloaded():
                        found_videos.append(video)

            return found_videos

        # Curate
        not_downloaded = []
        not_downloaded.extend(curate_list(self.videos, config.max_videos))
        not_downloaded.extend(curate_list(self.livestreams, config.max_livestreams))
        not_downloaded.extend(curate_list(self.shorts, config.max_shorts))

        return not_downloaded

    def _report_deleted(self, videos: Videos) -> None:
        """Goes through a video category to report & save those which where not marked in the metadata as deleted
         if they're not already known to be deleted"""
        for video in videos.inner.values():
            if not video.deleted.current() and not video.known_not_deleted:
                self.reporter.deleted.append(video)
                video.deleted.update(None, True)


def _skip_video(
    videos: list[Video],
    reason: str,
    warning: bool = False,
) -> tuple[list[Video], Video]:
    """Skips first un-downloaded video in `videos`, make sure there's at least one to skip otherwise
     an exception will be thrown"""
    # Find fist un-downloaded video
    for ind, video in enumerate(videos):
        if not video.downloaded():
            # Tell the user we're skipping over it
            if warning:
                logging.warning(
                    f"Skipping video {video.id} download for {video.archive} ({reason})"
                )
            else:
                logging.info(
                    f"Skipping video {video.id} download for {video.archive} ({reason})"
                )

            # Set videos to skip over this one
            videos = videos[ind+1:]

            # Return the corrected list and the video found
            return videos, video

    # Shouldn't happen, see docs
    raise Exception(
        "We expected to skip a video and return it but nothing to skip was found"
    )


def from_path(path: Path) -> Archive:
    content = path.read_text()

    match path.suffix:
        case '.json':
            content_dct = json.loads(content)
            return
        case _:
            raise NotImplementedError(f"Archive extension format '{path.suffix}' is not supported")

