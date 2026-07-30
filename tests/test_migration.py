"""Tests for migration helpers — _new_empty and archive version handling."""

from yark.core import Video, Element


class TestNewEmptyVideo:
    def test_creates_without_channel(self):
        video = Video._new_empty()
        assert video.id == "00000000"
        assert video.width == 0
        assert video.height == 0

    def test_all_elements_are_fresh(self):
        video = Video._new_empty()
        assert not video.title.changed()
        assert not video.description.changed()
        assert not video.views.changed()
        assert not video.likes.changed()
        assert not video.deleted.changed()

    def test_deleted_is_false(self):
        video = Video._new_empty()
        assert video.deleted.current() is False

    def test_known_not_deleted_is_false(self):
        video = Video._new_empty()
        assert video.known_not_deleted is False

    def test_element_can_be_serialized(self):
        """The whole point of _new_empty — it produces serializable elements."""
        video = Video._new_empty()
        el = Element.new(video, False)
        encoded = el._to_dict()
        decoded = Element._from_dict(encoded, video)
        assert decoded.current() is False
