"""Main runner for those using `python3 -m yark` instead of the proper `yark` script poetry provides"""
# Standard Imports
import sys

# Local Imports
import cli

# External Imports


cli.entry(sys.argv[1:])

