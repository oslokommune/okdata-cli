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
