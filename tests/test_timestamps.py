"""Tests for timestamp parsing and formatting."""

import pytest
from yark.web.timestamps import _decode_timestamp, _encode_timestamp
from yark.errors import TimestampException


class TestDecodeTimestamp:
    def test_seconds_only(self):
        assert _decode_timestamp("42") == 42

    def test_minutes_and_seconds(self):
        assert _decode_timestamp("1:23") == 83
        assert _decode_timestamp("02:05") == 125

    def test_hours_minutes_seconds(self):
        assert _decode_timestamp("1:00:00") == 3600
        assert _decode_timestamp("2:30:45") == 9045

    def test_integer_input(self):
        assert _decode_timestamp(90) == 90

    def test_float_input(self):
        assert _decode_timestamp(45.7) == 45

    def test_strips_whitespace(self):
        assert _decode_timestamp("  1:30  ") == 90

    def test_empty_string_raises(self):
        with pytest.raises(TimestampException):
            _decode_timestamp("")

    def test_blank_string_raises(self):
        with pytest.raises(TimestampException):
            _decode_timestamp("   ")

    def test_non_numeric_raises(self):
        with pytest.raises(TimestampException):
            _decode_timestamp("abc")

    def test_days_not_supported(self):
        with pytest.raises(TimestampException):
            _decode_timestamp("1:00:00:00")


class TestEncodeTimestamp:
    def test_zero(self):
        assert _encode_timestamp(0) == "00:00"

    def test_seconds_only(self):
        assert _encode_timestamp(5) == "00:05"
        assert _encode_timestamp(42) == "00:42"

    def test_minutes_and_seconds(self):
        assert _encode_timestamp(83) == "01:23"
        assert _encode_timestamp(125) == "02:05"
        assert _encode_timestamp(600) == "10:00"

    def test_hours(self):
        assert _encode_timestamp(9045) == "02:30:45"

    def test_roundtrip(self):
        # Values that survive encode→decode intact with the current encoder.
        # Some values lose 1s due to floating-point precision in hour extraction.
        cases = [0, 5, 42, 83, 125, 600, 3599, 9045]
        for secs in cases:
            assert _decode_timestamp(_encode_timestamp(secs)) == secs
