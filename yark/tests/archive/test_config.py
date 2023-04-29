# Standard Imports
import unittest
from pathlib import Path

# Local Imports
from yark import tests
from yark.yark.archiving.config.data import Config

# External Imports


class ConfigTestCase(unittest.TestCase):

    @unittest.skip
    def test_load(self):
        path = Path(f'{tests.__path__[0]}')

        result = Config()

        expected = Config(

        )

        self.assertEqual(expected, result)

