"""
Yark
====

YouTube archiving made simple.

Commonly-used
-------------

- `Channel`
    - `Config`
- `Video`
    - `Element`
    - `Note`
    - `Comment`
    - `CommentAuthor`
    - `Image`
- `viewer()`
- `ArchiveNotFoundException`
- `VideoNotFoundException`
- `NoteNotFoundException`
- `TimestampException`

Beware that using Yark as a library is currently experimental and breaking changes here are not tracked!
"""

from .channel import Channel
from .config import Config
from .video import (
    Video,
    Element,
    Note,
    Comment,
    CommentAuthor,
    Image,
)
from .viewer import viewer
from .errors import (
    ArchiveNotFoundException,
    VideoNotFoundException,
    NoteNotFoundException,
    TimestampException,
)
