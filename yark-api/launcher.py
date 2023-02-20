"""Launcher script for using the API in production; intended for use with pyinstaller and not used for development"""

from yark_api import create_app, config


def get_host(cfg: config.Config) -> str:
    """Gets host from `cfg` or returns default value"""
    if cfg.CUSTOM_HOST is not None:
        return cfg.CUSTOM_HOST
    return "127.0.0.1"


def get_port(cfg: config.Config) -> int:
    """Gets port from `cfg` or returns default value"""
    if cfg.CUSTOM_PORT is not None:
        return cfg.CUSTOM_PORT
    return 7666


app = create_app()
cfg = config.Config()
app.run(host=get_host(cfg), port=get_port(cfg))
