#!/usr/bin/env python3
"""
Cloud Downloader
"""

__author__ = "Baykam Say"
__version__ = "0.1.0"
__license__ = "Apache-2.0"

import argparse


def main(args):
    """ Main entry point of the app """
    print("hello world")
    print(vars(args))


class ParseCredentials(argparse.Action):
    """ Split username password into two """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values.split(":", 1))


if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument(
        "index_file", help="The URL of the index that includes the list of partial file locations and their authentication information")

    parser.add_argument(
        "username:password", action=ParseCredentials, help="The authentication information of the index server, in the structure <username>:<password>")

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)
