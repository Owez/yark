# Standard Imports
import threading
import webbrowser

# Local Imports

# External Imports
from yark.yark.viewer import viewer


def launch():
    """Launches viewer"""
    app = viewer()
    threading.Thread(target=lambda: app.run(port=7667)).run()


def open_general():
    print("Starting viewer..")
    webbrowser.open(f"http://127.0.0.1:7667/")
    launch()


def open_with_archive(archive_name: str):
    print(f"Starting viewer for {archive_name}..")
    webbrowser.open(f"http://127.0.0.1:7667/archive/{archive_name}/videos")
    launch()

