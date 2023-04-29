# Standard Imports
from pathlib import Path

# Local Imports
from yark_cli.archiver import _err_archive_not_found

# External Imports


def view(name: str):
    path = Path(name)

    if not path.exists():
        _err_archive_not_found()

    # TODO: Browser opening segment is possibly to be removed due to yark-pages introduction,
    #       ponder if CLI should be a entrypoint
    """
       browser.open_with_archive(args.name)
    else:
       browser.open_general()
    """
