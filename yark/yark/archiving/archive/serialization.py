# Standard Imports
from datetime import datetime
from pathlib import Path
import logging
import json

# Local Imports
from yark.yark.archiving.archive.data import archive
from yark.yark.archiving.config.data import config
from yark.yark.archiving.archive.data.archive import Archive
from yark.yark.exceptions import ArchiveNotFoundException


# External Imports


def from_path(path: Path) -> Archive:
    """Loads existing archive from path"""
    path = Path(path)
    archive_name = path.name

    logging.info(f"Loading {archive_name} archive")

    if not path.exists():
        raise ArchiveNotFoundException(path)

    encoded = config.from_path(path)

    return archive.from_archive_o(encoded, path)


def backup_archive(archive: Archive) -> None:
    """Creates a backup of the existing `yark.json` file in path as `yark.bak` with added comments"""
    logging.info(f"Creating a backup for {archive} as yark.bak")

    # Get current archive path
    archive_path = archive.path / "yark.json"

    # Skip backing up if the archive doesn't exist
    if not archive_path.exists():
        return

    # Open original archive to copy
    with open(archive_path.path / "yark.json", "r") as file_archive:
        # Add comment information to back-up file
        save = f"// Backup of a Yark archive, dated {datetime.utcnow().isoformat()}\n" \
               f"// Remove these comments and rename to 'yark.json' to restore\n" \
               f"{file_archive.read()}"

        # Save new information into a new backup
        with open(archive_path.path / "yark.bak", "w+") as file_backup:
            file_backup.write(save)


def commit_archive(archive: Archive, backup: bool = False) -> None:
    """Commits (saves) archive to path; do this once you've finished all of your transactions"""
    # Save backup if explicitly wanted
    if backup:
        backup_archive(archive)

    # Create resource directories if missing
    logging.info(f"Committing {archive} to file")

    """
    paths = [self.path, self.path / "images", self.path / "videos"]
    for path in paths:
        if not path.exists():
            path.mkdir()
    """

    map(
        lambda path: Path(path).mkdir,
        [archive.path, f'{archive.path}/images', f'{archive.path}/videos']
    )

    with open(archive.path / "yark.json", "w+") as file:
        json.dump(archive.to_archive_o(), file)
