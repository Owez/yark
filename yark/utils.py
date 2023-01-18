"""Useful shared utility constants, classes, and functions"""

IMAGE_AUTHOR_ICON = "jpg"
"""Image extension setting for all author icons"""

IMAGE_THUMBNAIL = "webp"
"""Image extension setting for all thumbnails"""

PYPI_VERSION = (1, 3)
"""Local PyPI version, using the proper way fails during development so it's best to hardcode"""

ARCHIVE_COMPAT = 4
"""
Version of Yark archives which this script is capable of properly parsing

- Version 1 was the initial format and had all the basic information you can see in the viewer now
- Version 2 introduced livestreams and shorts into the mix, as well as making the channel id into a general url
- Version 3 was a minor change to introduce a deleted tag so we have full reporting capability
- Version 4 introduced comments, moved `thumbnails/` to `images/` & changed how videos are stored

Some of these breaking versions are large changes and some are relatively small.
We don't check if a value exists or not in the archive format out of precedent
and we don't have optionally-present values, meaning that any new tags are a
breaking change to the format. The only downside to this is that the migrator
gets a line or two of extra code every breaking change. This is better than having
more complexity in the archiver decoding system itself.
"""


def _truncate_text(text: str, to: int = 31) -> str:
    """Truncates inputted `text` to ~32 length, adding ellipsis at the end if overflowing"""
    if len(text) > to:
        text = text[: to - 2].strip() + ".."
    return text.ljust(to)
