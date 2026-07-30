"""Tests for the Element model — the core time-series tracking primitive."""

from datetime import datetime, timedelta
from yark.core import Element


class TestElementCreation:
    def test_new_element(self, empty_video):
        el = Element.new(empty_video, "hello")
        assert el.current() == "hello"
        assert len(el.inner) == 1
        assert not el.changed()

    def test_new_element_numeric(self, empty_video):
        el = Element.new(empty_video, 1000)
        assert el.current() == 1000


class TestElementUpdate:
    def test_update_different_value(self, empty_video):
        el = Element.new(empty_video, "original")
        el.update("test kind", "changed")
        assert el.current() == "changed"
        assert el.changed()
        assert len(el.inner) == 2

    def test_update_same_value_does_nothing(self, empty_video):
        el = Element.new(empty_video, "same")
        el.update("test kind", "same")
        assert len(el.inner) == 1
        assert not el.changed()

    def test_update_without_kind_skips_report(self, empty_video):
        el = Element.new(empty_video, False)
        el.update(None, True)
        assert el.current() is True


class TestElementSerialization:
    def test_roundtrip_string(self, empty_video):
        el = Element.new(empty_video, "value")
        encoded = el._to_dict()
        decoded = Element._from_dict(encoded, empty_video)
        assert decoded.current() == "value"
        assert len(decoded.inner) == 1

    def test_roundtrip_with_changes(self, empty_video):
        el = Element.new(empty_video, 100)
        el.update("count", 200)
        el.update("count", 300)
        encoded = el._to_dict()
        decoded = Element._from_dict(encoded, empty_video)
        assert decoded.current() == 300
        assert len(decoded.inner) == 3
        assert decoded.changed()

    def test_roundtrip_preserves_timestamps(self, empty_video):
        el = Element.new(empty_video, "start")
        encoded = el._to_dict()
        decoded = Element._from_dict(encoded, empty_video)
        # The single timestamp key should match (within second precision)
        orig_key = list(el.inner.keys())[0]
        decoded_key = list(decoded.inner.keys())[0]
        assert abs((orig_key - decoded_key).total_seconds()) < 1


class TestElementCurrent:
    def test_current_returns_latest(self, empty_video):
        el = Element.new(empty_video, "first")
        el.update("test", "second")
        el.update("test", "third")
        assert el.current() == "third"

    def test_current_after_no_change(self, empty_video):
        el = Element.new(empty_video, 42)
        el.update("test", 42)  # same value
        assert el.current() == 42
        assert not el.changed()


class TestElementChanged:
    def test_unchanged_when_new(self, empty_video):
        el = Element.new(empty_video, "only")
        assert not el.changed()

    def test_changed_after_update(self, empty_video):
        el = Element.new(empty_video, "v1")
        el.update("test", "v2")
        assert el.changed()
