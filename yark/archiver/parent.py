"""Contextual information about parents of the current class"""

from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .archive import Archive
    from .video.video import Video
    from .video.comments import Comment
    from .video.comment_author import CommentAuthor
    from .video.element import Element


class Parent:
    archive: "Archive"
    video: Optional["Video"]
    element: Optional["Element"]
    comment: Optional["Comment"]
    comment_author: Optional["CommentAuthor"]

    @staticmethod
    def new_archive(archive: "Archive") -> Parent:
        """Adds an archive to the known stack, this is the most simple parent"""
        parent = Parent()
        parent.archive = archive
        return parent

    @staticmethod
    def new_video(archive: "Archive", video: "Video") -> Parent:
        """Adds a video to the known stack"""
        parent = Parent()
        parent.archive = archive
        parent.video = video
        return parent

    @staticmethod
    def new_element(archive: "Archive", element: "Element") -> Parent:
        """Adds a video to the known stack"""
        parent = Parent()
        parent.archive = archive
        parent.element = element
        return parent

    @staticmethod
    def new_comment(archive: "Archive", comment: "Comment") -> Parent:
        """Adds a comment to the known stack"""
        parent = Parent()
        parent.archive = archive
        parent.comment = comment
        return parent

    @staticmethod
    def new_comment_author(
        archive: "Archive", comment_author: "CommentAuthor"
    ) -> Parent:
        """Adds a comment author to the known stack"""
        parent = Parent()
        parent.archive = archive
        parent.comment_author = comment_author
        return parent
