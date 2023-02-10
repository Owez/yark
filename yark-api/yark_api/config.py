"""Configuration file for the Flask factory"""

import os
import sys


def get_env_ensure(key: str) -> str:
    """Definitely get an environment variable or errors out"""
    found = os.environ.get(key)
    if not found:
        print(f"Please provide the '{key}' environment variable", file=sys.stderr)
        sys.exit(1)
    return found


class Config:
    """Configuration state for launching the Flask app"""

    # Admin secret
    ADMIN_SECRET = get_env_ensure("YARK_SECRET")

    # Flask
    SECRET_KEY = os.environ.get("YARK_SECRET_FLASK")

    # SqlAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get("YARK_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask Caching
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300
