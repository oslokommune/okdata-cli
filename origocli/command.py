HELP = """usage: origo [command] <options>

  origo help
  origo [command] help
  origo [command] [subcommand] help

Commands available:
  datasets
  events
  help

Options
  --profile=<profile>
  --stage=<stage>
"""
from docopt import docopt
import logging
import json


class Command:
    def __init__(self, doc):
        if type(doc) is str:
            self.args = docopt(doc, version="Oslo Origo 1.0")
        else:
            self.args = doc
        debug = self.opt("debug")
        if debug:
            logging.basicConfig(level=logging.INFO)
        self.log = logging.getLogger()
        self.log.info(f"Creating command object from with arguments:\n {self.args}")

    def cmd(self, key):
        return self.args.get(key)

    def arg(self, key):
        return self.args.get(f"<{key}>", None)

    def opt(self, key):
        return self.args.get(f"--{key}", None)

    def print(self, str, payload=None):
        is_json = self.opt("format") == "json"
        if not is_json:
            print(str)
        # Normally a return json value from the API
        if payload and is_json:
            try:
                print(json.dumps(payload))
            except Exception:
                print(payload)
        elif payload:
            print(payload)

    def print_success(self, str):
        if self.opt("format") == "json":
            out = {}
            out["success"] = True
            out["message"] = str
            print(json.dumps(out))
        else:
            print(str)

    def no_data(self, str):
        if self.opt("format") == "json":
            print(f"{str}")

    def help():
        print(HELP)
