import json
import logging
import sys

from docopt import docopt, DocoptExit
from origo.sdk import SDK
from pygments import highlight, lexers, formatters


class BaseCommand:
    """usage:
  origo datasets [options]
  origo pipelines [options]
  origo events [options]
  origo event_streams [options]

Commands available:
  datasets
  pipelines
  events
  event_streams
  help

Options
  -d --debug
  --format=<format>
"""

    log = logging.getLogger(__name__)
    sub_commands = None
    args: dict
    handler: ()

    def __init__(self, sdk=None):
        self.args = docopt(str(self.__doc__))
        self.sdk = sdk
        if self.opt("debug"):
            logging.basicConfig(level=logging.DEBUG)
        if self.sdk is None:
            self.sdk = SDK(env=self.opt("env"))

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
        if payload and is_json:
            print(json.dumps(payload))

    @staticmethod
    def pretty_json(data):
        output = json.dumps(data, indent=2)
        colorful_json = highlight(
            output, lexers.JsonLexer(), formatters.TerminalFormatter()
        )
        print(colorful_json)

    @staticmethod
    def print_success(table, data=""):
        for row in data:
            table.add_row(row)
        print(table)

    def no_data(self, str):
        if self.opt("format") == "json":
            print(f"{str}")

    def help(self):
        print(self.__doc__, end="")

    def print_error_response(self, response_body):
        response_body.update({"error": 1})
        try:
            feedback = generate_error_feedback(
                message=response_body["message"], errors=response_body["errors"]
            )
        except KeyError:
            self.log.debug("Got unexpected response body from api.")
            self.print(response_body, payload=response_body)
        self.print(feedback, payload=response_body)


def generate_error_feedback(message, errors=None):
    feedback = f"\nOperation failed with message: {message}"
    if errors:
        feedback += f"\nCause:\n\t{errors}"

    return f"{feedback}\n"
