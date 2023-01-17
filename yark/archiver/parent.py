"""Contextual information about parents of the current class"""

from __future__ import annotations
from .archive import Archive
from typing import Optional, Any
from .video.video import Video
from .video.comments import Comment
from .video.comment_author import CommentAuthor


class Parent:
    archive: Archive
    video: Optional[Video]
    comment: Optional[Comment]
    comment_author = Optional[CommentAuthor]

    def __init__(self, archive: Archive) -> None:
        self.archive = archive

    def closest(self) -> Any:
        """Gets the closest parent for the known context"""
        # Comment author
        if self.comment_author is not None:
            return self.comment_author

        # Comment
        elif self.comment is not None:
            return self.comment

        # Video
        elif self.video is not None:
            return self.video

        # Just the archive
        return self.archive

    @staticmethod
    def new_video(archive: Archive, video: Video) -> Parent:
        """Adds a video to the known stack"""
        parent = Parent(archive)
        parent.video = video
        return parent

    @staticmethod
    def new_comment(archive: Archive, comment: Comment) -> Parent:
        """Adds a comment to the known stack, also factoring in video"""
        parent = Parent(archive)
        parent.comment = comment
        parent.video = comment.parent.video
        return parent

    @staticmethod
    def new_comment_author(archive: Archive, comment_author: CommentAuthor) -> Parent:
        """Adds a comment author to the known stack"""
        parent = Parent(archive)
        parent.comment_author = comment_author
        return parent
