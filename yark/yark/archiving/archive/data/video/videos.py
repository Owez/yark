# Standard Imports
from typing import Any, TYPE_CHECKING
from dataclasses import dataclass, field

# Local Imports
from yark.yark.archiving.archive.data import video
from yark.yark.exceptions import VideoNotFoundException

if TYPE_CHECKING:
    from yark.yark.archiving.archive.data import Archive
    from yark.yark.archiving.archiver import Videos
    from yark.yark.archiving.archive.data.video.data import Video

# External Imports


@dataclass(init=True, slots=True)
class Videos:
    archive: 'Archive'
    inner: dict[str, 'Video'] = field(default_factory=dict)

    def sort(self) -> None:
        """Sorts `inner` videos content by newest date uploaded"""
        sorted_kv = sorted(
            self.inner.items(), key=lambda item: item[1].uploaded, reverse=True
        )
        sorted_dict = {k: v for k, v in sorted_kv}
        self.inner = sorted_dict

    def search(self, kind: str) -> 'Video':
        """Gets a video inside the list via it's identifier or raises ``"""
        found = self.inner.get(kind)

        if found is not None:
            return found

        raise VideoNotFoundException()

    @staticmethod
    def from_archive_o(archive: 'Archive', entry: dict[str, dict[str, Any]]) -> 'Videos':
        """Loads videos from its object in the archive"""
        videos = Videos(archive)

        for kind in entry.keys():
            videos.inner[kind] = video.data._from_archive_ib(archive, kind, entry[kind])

        return videos

    def to_archive_o(self) -> dict[str, dict[str, Any]]:
        """Saves each video as an id & body style dict inside a videos object"""
        payload = {}

        for kind in self.inner:
            payload[kind] = video._to_archive_b(self.inner[kind])

        return payload
