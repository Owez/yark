# Standard Imports
from typing import Protocol

# Local Imports

# External Imports


class Data(Protocol):
    ...


class Schema(Protocol):
    migrator: 'Migrator'


class Migrator(Protocol):

    previous_version: Schema | None
    next_version: Schema | None

    def upgrade(self, schema: Schema) -> Schema:
        ...

    def downgrade(self, schema: Schema) -> Schema:
        ...

    @staticmethod
    def upgrade_recursive(schema: Schema) -> Schema:
        """Updates to the latest version possible, by recurse upgrading through schemas"""

        next_schema: Schema | None = None
        while next_schema.migrator.next_version:
            next_schema = schema.migrator.upgrade(schema)

        return schema

    @staticmethod
    def downgrade_recursive(schema: Schema) -> Schema:
        """Downgrades to the oldest version possibly, by recurse downgrading through schemas"""
        # raise NotImplementedError
        ...

