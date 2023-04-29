# Standard Imports
from dataclasses import dataclass

# Local Imports
from yark.archiving.archiver.migration import Schema, Migrator

# External Imports


@dataclass(order=True, slots=True)
class ArchiveV3Schema(Schema):
    pass


class V3Migrator(Migrator):
    pass

