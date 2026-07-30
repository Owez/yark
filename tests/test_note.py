"""Tests for the Note model — creation, serialization, and search."""

import pytest
from yark.core import Note, Video
from yark.errors import NoteNotFoundException


class TestNoteCreation:
    def test_new_note_minimal(self, empty_video):
        note = Note.new(empty_video, 42, "My timestamp")
        assert note.title == "My timestamp"
        assert note.timestamp == 42
        assert note.body is None
        assert len(note.id) == 36  # UUID4

    def test_new_note_with_body(self, empty_video):
        note = Note.new(empty_video, 120, "A moment", "This part was interesting")
        assert note.title == "A moment"
        assert note.timestamp == 120
        assert note.body == "This part was interesting"


class TestNoteSerialization:
    def test_roundtrip_minimal(self, empty_video):
        note = Note.new(empty_video, 42, "Test note")
        encoded = note._to_dict()
        decoded = Note._from_dict(empty_video, encoded)
        assert decoded.id == note.id
        assert decoded.timestamp == note.timestamp
        assert decoded.title == note.title
        assert decoded.body == note.body

    def test_roundtrip_with_body(self, empty_video):
        note = Note.new(empty_video, 90, "Timeline", "Some body text")
        encoded = note._to_dict()
        decoded = Note._from_dict(empty_video, encoded)
        assert decoded.body == "Some body text"

    def test_roundtrip_none_body(self, empty_video):
        note = Note.new(empty_video, 30, "No body here")
        encoded = note._to_dict()
        decoded = Note._from_dict(empty_video, encoded)
        assert decoded.body is None


class TestVideoNoteSearch:
    def test_search_finds_note(self, empty_video):
        note = Note.new(empty_video, 60, "Find me")
        empty_video.notes.append(note)
        found = empty_video.search(note.id)
        assert found is note
        assert found.title == "Find me"

    def test_search_raises_for_missing(self, empty_video):
        with pytest.raises(NoteNotFoundException):
            empty_video.search("nonexistent-id")

    def test_search_among_multiple(self, empty_video):
        a = Note.new(empty_video, 10, "First")
        b = Note.new(empty_video, 20, "Second")
        c = Note.new(empty_video, 30, "Third")
        empty_video.notes.extend([a, b, c])
        assert empty_video.search(b.id) is b
