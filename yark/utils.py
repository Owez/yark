"""Useful shared utility constants, classes, and functions"""

IMAGE_AUTHOR_ICON = "jpg"
"""Image extension setting for all author icons"""

IMAGE_THUMBNAIL = "webp"
"""Image extension setting for all thumbnails"""

PYPI_VERSION = (1, 3)
"""Local PyPI version, using the proper way fails during development so it's best to hardcode"""


def _truncate_text(text: str, to: int = 31) -> str:
    """Truncates inputted `text` to ~32 length, adding ellipsis at the end if overflowing"""
    if len(text) > to:
        text = text[: to - 2].strip() + ".."
    return text.ljust(to)
