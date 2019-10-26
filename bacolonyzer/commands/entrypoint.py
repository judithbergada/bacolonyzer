#!/usr/bin/env python3

import argparse

import bacolonyzer
from bacolonyzer import commands


# Entrypoint from the command line.
def run():
    # Create main inputs parser.
    parser = argparse.ArgumentParser(
        description="""Commands and tools for the analysis of QFA images.""")
    # Add version argument.
    parser.add_argument(
        "-v",
        "--version",
        help="show current version",
        action='version',
        version="BaColonyzer {}".format(bacolonyzer.__version__))

    # Register all possible commands of BaColonyzer to the main inputs parser.
    subparsers = parser.add_subparsers()
    commands.AnalyseCommand().register_parser(subparsers)
    commands.RenameImagesCommand().register_parser(subparsers)

    # Actually parsing the inputs given by the user.
    options = parser.parse_args()
    # Execute the run functions depending on the command given on the terminal.
    options.func(options)
