# Standard Imports
import os
import unittest

# Local Imports

# External Imports
from yark_cli import new_cli, ReportCode


class CLITestCase(unittest.TestCase):

    def test_new_command(self):
        args = [
            'new', 'some', 'https://www.youtube.com/channel/UCiLqeNEXxc8ny7GfzEzCLDQ',
            '-o', f'{os.getcwd()}/_data_/archives/'
        ]

        with self.assertRaises(SystemExit) as cm:
            new_cli.entry.main(args)

        self.assertEqual(ReportCode.Ok, cm.exception.code)

    def test_refresh_command(self):
        args = ['refresh', 'some']

        with self.assertRaises(SystemExit) as cm:
            new_cli.entry.main(args)

        self.assertEqual(ReportCode.Ok, cm.exception.code)

    def test_report_command(self):
        args = ['report', 'some']

        with self.assertRaises(SystemExit) as cm:
            new_cli.entry.main(args)

        self.assertEqual(ReportCode.Ok, cm.exception.code)


