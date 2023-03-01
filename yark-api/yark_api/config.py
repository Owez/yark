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


def get_custom_port() -> int | None:
    """Converts custom port value to an integer or returns an error"""
    ENV_KEY = "YARK_PORT"
    var = os.environ.get(ENV_KEY)
    if var is None:
        return var
    try:
        out = int(var)
        if out < 0 or out > 65565:
            raise Exception()
        return out
    except:
        print(
            "Please provide a valid port number for the '{ENV_KEY}' environment variable",
            file=sys.stderr,
        )
        sys.exit(1)


class Config:
    """Configuration state for launching the Flask app"""

    # Host and port config
    CUSTOM_HOST: str | None
    CUSTOM_PORT: int | None

    # Admin secret
    ADMIN_SECRET: str

    # Flask
    SECRET_KEY: str | None

    # SqlAlchemy
    SQLALCHEMY_DATABASE_URI: str | None
    SQLALCHEMY_TRACK_MODIFICATIONS: bool

    # Flask Caching
    CACHE_TYPE: str
    CACHE_DEFAULT_TIMEOUT: int

    def __init__(self) -> None:
        self.CUSTOM_HOST = os.environ.get("YARK_HOST")
        self.CUSTOM_PORT = get_custom_port()
        self.ADMIN_SECRET = get_env_ensure("YARK_ADMIN_SECRET")
        self.SECRET_KEY = os.environ.get("YARK_SECRET_FLASK")
        self.SQLALCHEMY_DATABASE_URI = os.environ.get("YARK_DATABASE_URI")
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.CACHE_TYPE = "SimpleCache"
        self.CACHE_DEFAULT_TIMEOUT = 300
