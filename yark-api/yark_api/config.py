"""Configuration file for the Flask factory"""

import os


class Config:
    """Configuration state for launching the Flask app"""

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # SqlAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask Caching
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300
