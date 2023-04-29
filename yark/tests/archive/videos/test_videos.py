# Standard Imports
import unittest

# Local Imports
from yark.archiving.archiver.video.videos import Videos

# External Imports


class VideosTestCase(unittest.TestCase):

    @unittest.skip
    def test_load(self):
        raise NotImplementedError

    @unittest.skip
    def test_to_archive_object(self):
        video = Videos()
        result = video.to_archive_o()

        expected = {

        }

        self.assertEqual(expected, result)

    @unittest.skip
    def test_from_archive_object(self):
        videos = Videos()
        result = videos.from_archive_ib()

        expected = {

        }

        self.assertEqual(expected, result)

