"""
Yark API
========

Official REST API for Yark archive management
"""

from flask import Flask
from . import extensions
from . import config


def create_app() -> Flask:
    """Creates a new Flask app to launch"""
    # Create app foundation
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config.Config())

    # Integrate extensions
    extensions.db.init_app(app)

    # Hand app over
    return app
