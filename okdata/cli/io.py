import json
import logging
import os
import sys

log = logging.getLogger()


def read_json(filename=None):
    """Read JSON data from a file named `filename`.

    If no filename is given, the data is read from stdin instead.
    """
    if filename:
        log.info(f"Reading data from file: {filename}")
        with open(os.path.expanduser(filename)) as f:
            return json.load(f)

    log.info("Reading data from stdin")
    return json.loads(sys.stdin.read())


def resolve_output_filepath(target):
    path_components = target.split("/")
    if path_components[0] == ".":
        path_components[0] = os.getcwd()
    if path_components[-1] == "":
        path_components.pop()

    return "/".join(path_components)
