"""
Yark API
========

YouTube archiving made simple (REST API)

See https://github.com/Owez/yark/tree/master/yark-api for more information
"""

from flask import Flask
from . import extensions
from . import config
from .routes.archive import ArchiveResource, SpecificArchiveResource
from .routes.misc import IndexResource
from .routes.video import SpecificVideoResource
from .routes.thumbnail import SpecificThumbnailResource
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
    extensions.api.add_resource(SpecificArchiveResource, "/archive/<string:slug>")
    extensions.api.add_resource(
        SpecificVideoResource, "/archive/<string:slug>/video/<string:id>"
    )
    extensions.api.add_resource(
        SpecificThumbnailResource, "/archive/<string:slug>/thumbnail/<string:id>"
    )

    # Integrate extensions
    extensions.db.init_app(app)
    extensions.api.init_app(app)
    extensions.cache.init_app(app)
    extensions.cors.init_app(app)

    # Hand app over
    return app
