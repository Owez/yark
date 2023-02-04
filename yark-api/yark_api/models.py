"""Database models for long-term CRUD operations"""

from .extensions import db

ARCHIVE_MAX_SLUG = 32
ARCHIVE_MAX_PATH = 4096


class Archive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(ARCHIVE_MAX_SLUG), unique=True, nullable=False)
    path = db.Column(db.String(ARCHIVE_MAX_PATH), nullable=False)
    metadata_queue = db.relationship("MetadataQueue", backref="archive")
    download_queue = db.relationship("DownloadQueue", backref="archive")


class MetadataQueue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    archive_id = db.Column(db.Integer, db.ForeignKey("archive.id"), nullable=False)


class DownloadQueue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    archive_id = db.Column(db.Integer, db.ForeignKey("archive.id"), nullable=False)
