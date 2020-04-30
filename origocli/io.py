import sys
import json
import logging

log = logging.getLogger()


def read_stdin_or_filepath(file):
    payload = None
    if file is not None:
        log.info(f"Reading data from file: {file}")
        with open(file) as f:
            payload = json.load(f)
    else:
        log.info("Reading data from stdin")
        data = ""
        for i, dataline in enumerate(sys.stdin, start=1):
            data = f"{data}\n{dataline}"
        payload = json.loads(data)
    # TODO: raise DataNotFoundException()
    return payload
