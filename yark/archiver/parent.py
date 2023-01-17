"""Contextual information about parents of the current class"""

from __future__ import annotations
from .archive import Archive
from typing import Optional
from .video.video import Video
from .video.comments import Comment
from .video.comment_author import CommentAuthor
from .video.element import Element


class Parent:
    archive: Archive
    video: Optional[Video]
    element: Optional[Element]
    comment: Optional[Comment]
    comment_author = Optional[CommentAuthor]

    def __init__(self, archive: Archive) -> None:
        self.archive = archive

    @staticmethod
    def new_video(archive: Archive, video: Video) -> Parent:
        """Adds a video to the known stack"""
        parent = Parent(archive)
        parent.video = video
        return parent

    @staticmethod
    def new_element(archive: Archive, element: Element) -> Parent:
        """Adds a video to the known stack"""
        parent = Parent(archive)
        parent.element = element
        return parent

    @staticmethod
    def new_comment(archive: Archive, comment: Comment) -> Parent:
        """Adds a comment to the known stack"""
        parent = Parent(archive)
        parent.comment = comment
        return parent

    @staticmethod
    def new_comment_author(archive: Archive, comment_author: CommentAuthor) -> Parent:
        """Adds a comment author to the known stack"""
        parent = Parent(archive)
        parent.comment_author = comment_author
        return parent
