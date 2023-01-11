"""
Yark
====

YouTube archiving made simple.

Commonly-used
-------------

- `Channel`
    - `DownloadConfig`
- `Video`
    - `Element`
    - `Note`
    - `Thumbnail`
- `viewer()`
- `ArchiveNotFoundException`
- `VideoNotFoundException`
- `NoteNotFoundException`
- `TimestampException`

Beware that using Yark as a library is currently experimental and breaking changes here are not tracked!
"""

from .channel import Channel, DownloadConfig
from .video import Video, Element, Note, Thumbnail
from .viewer import viewer
from .errors import (
    ArchiveNotFoundException,
    VideoNotFoundException,
    NoteNotFoundException,
    TimestampException,
)
