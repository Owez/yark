"""Configuration file for the Flask factory"""

import os


class Config:
    """Configuration state for launching the Flask app"""

    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
