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

Beware that Yark is primarily cli-focused and doesn't guarantee stability between versions if you're using it as a module!
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
