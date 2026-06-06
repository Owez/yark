"""Flask application factory for the offline archive viewer."""

import logging
from pathlib import Path

from flask import Flask

from .routes import routes
from .timestamps import _encode_timestamp

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"


def create_app() -> Flask:
    """Generates the Flask app for the offline viewer."""
    # Make flask app
    app = Flask(__name__, template_folder=str(TEMPLATES_DIR))

    # Only log errors
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    # Routing blueprint
    app.register_blueprint(routes)

    @app.template_filter("timestamp")
    def _jinja2_filter_timestamp(timestamp, fmt=None):
        """Special hook for timestamps"""
        return _encode_timestamp(timestamp)

    # Return
    return app