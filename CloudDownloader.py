#!/usr/bin/env python3
"""
Cloud Downloader
"""

__author__ = "Baykam Say"
__version__ = "0.1.0"
__license__ = "Apache-2.0"

import argparse
import base64
import concurrent.futures
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


def recv_body(s, start, end_index):
    """ Reads from where recv_header left off until the end of body """
    res = start
    buffer = b""
    iterations = 0
    try:
        while len(res) < end_index:
            iterations += 1
            buffer = s.recv(BUFLEN)
            # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Iteration: %r\n%s\n\n\n" %
            #       (iterations, buffer.decode()))
            if not buffer:
                break
            else:
                res += buffer
    except socket.timeout:
        print("\n\n\n~~~~~~~~~~~~~TIMEOUT~~~~~~~~~~~~~\n\n\n")
        pass
    print(iterations)
    return res


def get_partial(url, cred, offset, end):
    """
    Requests a partial txt file and returns the start-end portion of the body
    """
    HOST, PATH = url.rstrip().split("/", 1)
    PATH = "/" + PATH
    credentials = str(base64.b64encode(
        bytes(cred, encoding="ascii")), encoding="ascii")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        req = (
            f"GET {PATH} HTTP/1.1\r\n"
            f"Host: {HOST}\r\n"
            f"Authorization: Basic {credentials}\r\n"
            "\r\n"
        )
        s.sendall(bytes(req, encoding="ascii"))
        res = recv_header(s)
        header_res, body_start = split_header(res)
        header = header_res.decode()
        body_res = recv_body(s, body_start, get_content_length(header))
    return body_res[offset:end]


def get_all_partials(data):
    """
    Requests all partial txt files in the given data returns the resulting text 
    file name, size, and partials
    """
    lines = data.rstrip().split("\n")
    partial_lines = lines[2:]
    partials = [partial_lines[n:n+3] for n in range(0, len(partial_lines), 3)]
    urls = []
    creds = []
    offsets = []
    ends = []
    prev_end = 0
    for partial in partials:
        start, end = partial[2].split("-", 1)
        start, end = int(start), int(end)
        urls.append(partial[0])
        creds.append(partial[1])
        offsets.append(prev_end-start+1)
        ends.append(end-start+1)
        prev_end = end

    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = executor.map(get_partial, urls, creds, offsets, ends)

    return (lines[0], lines[1], result)


def main(args):
    """ Main entry point """
    url = vars(args)["index_file"]
    HOST, PATH = url.split("/", 1)  # use urllib.parse for better parsing
    PATH = "/" + PATH
    credentials = str(base64.b64encode(
        bytes(vars(args)["username:password"], encoding="ascii")), encoding="ascii")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        req = (
            f"GET {PATH} HTTP/1.1\r\n"
            f"Host: {HOST}\r\n"
            f"Authorization: Basic {credentials}\r\n"
            "\r\n"
        )
        s.sendall(bytes(req, encoding="ascii"))
        res = recv_header(s)
        header_res, body_start = split_header(res)
        header = header_res.decode()
        body_res = recv_body(s, body_start, get_content_length(header))
    body = body_res.decode()
    filename, filesize, data = get_all_partials(body)
    result_string = (b"".join(data)).decode()
    with open(filename, "w+") as result_file:
        result_file.write(result_string)


if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument(
        "index_file", help="The URL of the index that includes the list of partial file locations and their authentication information")

    parser.add_argument(
        "username:password", help="The authentication information of the index server, in the structure <username>:<password>")

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)
