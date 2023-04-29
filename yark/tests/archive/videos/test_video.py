# Standard Imports
import unittest

# Local Imports
from yark.archiving.archiver.video.data import Video

# External Imports


class VideoTestCase(unittest.TestCase):

    @unittest.skip
    def test_load(self):
        result = Video()

        expected = Video(

        )

        self.assertEqual(expected, result)
