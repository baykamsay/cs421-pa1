#!/usr/bin/env python3
"""
Cloud Downloader
"""

__author__ = "Baykam Say"
__version__ = "0.1.0"
__license__ = "Apache-2.0"

import argparse
import socket

PORT = 80
BUFLEN = 4096


def recv_header(s):
    """ Read until header is finished """
    res = b""
    buffer = b""
    try:
        while not b"\r\n\r\n" in buffer:
            buffer = s.recv(BUFLEN)
            if not buffer:
                break
            else:
                res += buffer
    except socket.timeout:
        pass
    return res


def split_header(res):
    """ Split the header and the start of the body """
    try:
        header_end = res.index(b"\r\n\r\n") + len(b"\r\n\r\n")
    except:
        return res, b""
    else:
        return res[:header_end], res[header_end:]


def get_content_length(header):
    """ Gets the Content-Length from a given ascii header """
    header = header.split("\r\n")
    for line in header:
        if "Content-Length" in line:
            return int(line[line.index(":")+1:])


def recv_body(s, body_start, start, end):
    """ Reads from where recv_header left off until the end of body """
    res = body_start
    buffer = b""
    length = start
    try:
        while length < end:
            buffer = s.recv(BUFLEN)
            if not buffer:
                break
            else:
                res += buffer
    except socket.timeout:
        pass
    return res


def main(args):
    """ Main entry point of the app """
    url = vars(args)["index_file"]
    HOST, PATH = url.split("/", 1)  # use urllib.parse for better parsing
    PATH = "/" + PATH

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        req = (
            f"GET {PATH} HTTP/1.1\r\n"
            f"Host: {HOST}\r\n"
            "\r\n"
        )
        s.sendall(bytes(req, encoding="ascii"))
        res = recv_header(s)
        header_res, body_res = split_header(res)
        header = header_res.decode()
        body_res = recv_body(s, body_res, len(header_res),
                             get_content_length(header))
        body = body_res.decode()
        print(body)


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
