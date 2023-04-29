# Standard Imports
from pathlib import Path

# Local Imports
from yark.archiver.archive import Archive

# External Imports


def report(name: str):
    try:
        report_archive = Archive.load(Path(name))
        report_archive.reporter.interesting_changes()
    except Exception as ex:
        # TODO
        pass

