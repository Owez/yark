# Standard Imports

# Local Imports
from yark.versioning import pypi

# External Imports


def check_version():
    # Version announcements before going further
    try:
        pypi.check_version_upstream()
    except Exception as err:
        # TODO: Address logging uniformization and replace here with the right usage
        """
        logger.err_msg(
            f"Error: Failed to check for new Yark version, info:\n"
            + Style.NORMAL
            + str(err)
            + Style.BRIGHT,
            True,
        )
        """

        return False

    return True
