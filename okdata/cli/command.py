import json
import logging
import sys

from docopt import docopt, DocoptExit
from okdata.sdk import SDK
from pygments import highlight, lexers, formatters

BASE_COMMAND_OPTIONS = """
  -h, --help                # Print this help
  -d, --debug               # Output debug information while executing task
  --format=<value>          # Output format: table OR json
  --env=<value>             # Environment to run command in: prod OR dev"""


class BaseCommand:
    __doc__ = f"""usage:
  okdata datasets [options]
  okdata status [options]
  okdata pipelines [options]
  okdata events [options]
  okdata permissions [options]
  okdata webhooks [options]
  okdata -h | --help

Commands available:
  datasets
  status
  pipelines
  events
  permissions
  webhooks

Options:{BASE_COMMAND_OPTIONS}
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
        if payload:
            # If it is a pure dict or list we want to json dump it out in order to correctly
            # use it together with jq on the commandline
            if isinstance(payload, dict) or isinstance(payload, list):
                print(json.dumps(payload))
            else:
                print(payload)

    def login(self):
        self.sdk.login()

    @staticmethod
    def pretty_json(data):
        output = json.dumps(data, indent=2)
        colorful_json = highlight(
            output, lexers.JsonLexer(), formatters.TerminalFormatter()
        )
        print(colorful_json)

    @staticmethod
    def print_success(table, data=[]):
        for row in data:
            table.add_row(row)
        print(table)

    def no_data(self, str):
        if self.opt("format") == "json":
            print(f"{str}")

    def help(self):
        print(self.__doc__, end="")

    def print_error_response(self, response_body):
        if type(response_body) != dict:
            print(response_body)
            return

        response_body.update({"error": 1})

        if self.opt("format") == "json":
            print(json.dumps(response_body))
        else:
            try:
                feedback = generate_error_feedback(
                    message=response_body["message"],
                    errors=response_body.get("errors", None),
                )
                print(feedback)
            except KeyError:
                self.log.debug("Got unexpected response body from api.")
                print(response_body)


def generate_error_feedback(message, errors=None):
    feedback = f"An error occured: {message}"
    if errors:
        feedback += f"\nCause:\n\t{errors}"

    return f"{feedback}"
