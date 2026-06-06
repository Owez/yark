"""Timestamp parsing and formatting helpers for the web layer."""

from ..errors import TimestampException


def _decode_timestamp(input: str) -> int:
    """Parses timestamp into seconds or raises `TimestampException`"""
    # Check existence
    input = input.strip()
    if input == "":
        raise TimestampException("No input provided")

    # Split colons
    splitted = input.split(":")
    splitted.reverse()
    if len(splitted) > 3:
        raise TimestampException("Days and onwards aren't supported")

    # Parse
    secs = 0
    try:
        # Seconds
        secs += int(splitted[0])

        # Minutes
        if len(splitted) > 1:
            secs += int(splitted[1]) * 60

        # Hours
        if len(splitted) > 2:
            secs += int(splitted[2]) * 60 * 60
    except:
        raise TimestampException("Only numbers are allowed in timestamps")

    # Return
    return secs


def _encode_timestamp(timestamp: int) -> str:
    """Formats previously parsed human timestamp for notes, e.g. `02:25`"""
    # Collector
    parts = []

    # Hours
    if timestamp >= 60 * 60:
        # Get hours float then append truncated
        hours = timestamp / (60 * 60)
        parts.append(str(int(hours)).rjust(2, "0"))

        # Remove truncated hours from timestamp
        timestamp = int((hours - int(hours)) * 60 * 60)

    # Minutes
    if timestamp >= 60:
        # Get minutes float then append truncated
        minutes = timestamp / 60
        parts.append(str(int(minutes)).rjust(2, "0"))

        # Remove truncated minutes from timestamp
        timestamp = int((minutes - int(minutes)) * 60)

    # Seconds
    if len(parts) == 0:
        parts.append("00")
    parts.append(str(timestamp).rjust(2, "0"))

    # Return
    return ":".join(parts)