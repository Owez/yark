"""Launcher stub workaround for pyinstaller #2560 <https://github.com/pyinstaller/pyinstaller/issues/2560>"""

from yark import cli

if __name__ == "__main__":
    cli._cli()
