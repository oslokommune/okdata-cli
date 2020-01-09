import json
import logging
import sys

from docopt import docopt, DocoptExit
from origo.sdk import SDK
from pygments import highlight, lexers, formatters


class BaseCommand:
    """usage:
  origo [command] <options>
  origo help
  origo [command] help
  origo [command] [subcommand] help

Commands available:
  datasets
  pipelines
  events
  help

Options
  --profile=<profile>
  --stage=<stage>
"""

    log = logging.getLogger(__name__)
    sub_commands = None
    args: dict
    handler: ()
    sdk = SDK()

    def __init__(self):
        self.args = docopt(str(self.__doc__))
        if self.opt("debug"):
            logging.basicConfig(level=logging.DEBUG)

    def handle(self):
        self.args = docopt(str(self.__doc__))
        if self.sub_commands:
            for cmd in self.sub_commands:
                try:
                    self.log.debug(f"Checking if sub_command '{cmd.__name__}' is valid")
                    return cmd(self.sdk).handle()
                except DocoptExit as d:
                    self.log.debug(d.usage)
                    continue

        if not hasattr(self, "handler"):
            self.log.info("command was implemented without a default handler")
            print(self.__doc__)
            return None
        return self.handler()

    def cmd(self, key):
        return self.args.get(key)

    def arg(self, key):
        return self.args.get(f"<{key}>", None)

    def opt(self, key):
        return self.args.get(f"--{key}", None)

    def handle_input(self):
        if self.cmd("-"):
            content = sys.stdin.read()
        else:
            with open(self.arg("file")) as f:
                content = f.read()
        return content

    def print(self, str, payload=None):
        is_json = self.opt("format") == "json"
        if not is_json:
            print(str)
        # Normally a return json value from the API
        if payload:
            print(payload)

    def pretty_json(self, data):
        output = json.dumps(data, indent=2)
        colorful_json = highlight(
            output, lexers.JsonLexer(), formatters.TerminalFormatter()
        )
        print(colorful_json)

    def print_success(self, table, data):
        for row in data:
            table.add_row(row)
        print(table)

    def no_data(self, str):
        if self.opt("format") == "json":
            print(f"{str}")

    @staticmethod
    def help():
        print(BaseCommand.__doc__)
