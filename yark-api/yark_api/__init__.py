"""
Yark API
========

Official REST API for Yark archive management
"""

from flask import Flask
from . import extensions
from . import config
from .routes.archive import ArchiveResource
from .routes.misc import IndexResource
import logging


def create_app() -> Flask:
    """Creates a new Flask app to launch"""
    logging.info("Creating app to launch")

    # Create app foundation
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config.Config())

    # Add resources to routes
    extensions.api.add_resource(IndexResource, "/")
    extensions.api.add_resource(ArchiveResource, "/archive")

    # Integrate extensions
    extensions.db.init_app(app)
    extensions.api.init_app(app)
    extensions.cache.init_app(app)

    # Hand app over
    return app
