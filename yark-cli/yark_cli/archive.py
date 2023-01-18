# Standard Imports
from pathlib import Path

# Local Imports

# External Imports
from yark.yark.archiver.archive import Archive
from yark.yark.archiver.config import Config
from yark.yark.cli import _err_archive_not_found
from yark.yark.errors import ArchiveNotFoundException


def archive_do(config: Config, path: Path):
    try:
        archive = Archive.load(path)

        if config.skip_metadata:
            print("Skipping metadata download..")
        else:
            archive.metadata(config)
            archive.commit(True)

        if config.skip_download:
            print("Skipping videos/livestreams/shorts download..")
        else:
            archive.download(config)
            archive.commit()

        archive.reporter.print()
    except ArchiveNotFoundException:
        _err_archive_not_found()

