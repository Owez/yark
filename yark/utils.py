"""Useful shared utility functions"""


def _truncate_text(text: str, to: int = 31) -> str:
    """Truncates inputted `text` to ~32 length, adding ellipsis at the end if overflowing"""
    if len(text) > to:
        text = text[: to - 2].strip() + ".."
    return text.ljust(to)
