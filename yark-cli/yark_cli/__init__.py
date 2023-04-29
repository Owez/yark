# Standard Imports
import enum

# Local Imports

# External Imports


class ReportCode(enum.IntEnum):
    Ok = 0  # All okay
    VersionMismatch = enum.auto()  # When the version upstream doesn't match the current one
    FailedReport = enum.auto()  # When an archive report analysis fails
