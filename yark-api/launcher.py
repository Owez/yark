"""Launcher script for using the API in production; intended for use with pyinstaller"""

from yark_api import create_app

app = create_app()
app.run("127.0.0.1", 7666)
