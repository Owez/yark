# Standard Imports
import unittest

# Local Imports

# External Imports


class Comment(unittest.TestCase):

    def test_load(self):
        comment = Comment()

        expected = Comment()

        self.assertEqual(expected, comment)
