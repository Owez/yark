# Standard Imports
import unittest

# Local Imports
import tests

# External Imports
from yark.yark.archiving.archive.data.archive import Archive
from yark.yark.archiving.archive import serialization


class ArchiveTestCase(unittest.TestCase):

    def test_create(self):
        new_archive = Archive(tests.archive.archive_path, tests.archive.channel_url)
        serialization.commit_archive(new_archive)

        self.assertTrue(tests.archive.archive_path.exists())

    def test_load(self):
        result = serialization.from_path(tests.archive.archive_path)
        expected = Archive(tests.archive.archive_path, tests.archive.channel_url)

        self.assertEqual(expected, result)

