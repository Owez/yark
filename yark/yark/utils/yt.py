# Standard Imports
from datetime import datetime

# Local Imports

# External Imports


def _decode_date_yt(date: str) -> datetime:
    """Decodes date from YouTube like `20180915` for example"""
    return datetime.strptime(date, "%Y%m%d")


def _encode_date_human(date: datetime) -> str:
    """Encodes an `input` date into a standardized human-readable format"""
    return date.strftime("%d %b %Y")


def _magnitude(count: int | None = None) -> str:
    """Displays an integer as a sort of ordinal order of magnitude"""
    if count is None:
        return "?"
    elif count < 1000:
        return str(count)
    elif count < 1000000:
        value = "{:.1f}".format(float(count) / 1000.0)
        return value + "k"
    elif count < 1000000000:
        value = "{:.1f}".format(float(count) / 1000000.0)
        return value + "m"
    else:
        value = "{:.1f}".format(float(count) / 1000000000.0)
        return value + "b"

