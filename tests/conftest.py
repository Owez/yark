"""Shared fixtures for the Yark test suite."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock
from yark.core import Video


class _MockReporter:
    """Reporter stand-in that records calls without side effects."""
    def __init__(self):
        self.added = []
        self.deleted = []
        self.updated = []

    def add_updated(self, kind, element):
        self.updated.append((kind, element))

    def reset(self):
        self.added = []
        self.deleted = []
        self.updated = []


class _MockChannel:
    """Minimal channel stand-in so Elements can report updates."""
    def __init__(self):
        self.reporter = _MockReporter()
        self.path = None


@pytest.fixture
def empty_video():
    """Video object with a mock channel, usable for Element, Note, and
    serialization tests without touching the filesystem."""
    video = Video()
    video.channel = _MockChannel()
    video.id = "test0000"
    video.uploaded = datetime(2024, 1, 15)
    video.width = 1920
    video.height = 1080
    video.notes = []
    video.known_not_deleted = False
    return video
