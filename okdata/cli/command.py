import json
import logging
import sys
from importlib import metadata

from docopt import docopt, DocoptExit
from okdata.sdk import SDK

BASE_COMMAND_OPTIONS = """
  -h, --help                # Print this help
  -d, --debug               # Output debug information while executing task
  --format=<value>          # Output format: table OR json
  --env=<value>             # Environment to run command in: prod OR dev"""


class BaseCommand:
    version = metadata.version("okdata-cli")

    __doc__ = f"""okdata-cli {version}

usage:
  okdata datasets [options]
  okdata permissions [options]
  okdata pubreg [options]
  okdata status [options]
  okdata teams [options]
  okdata -h | --help

Commands available:
  datasets
  permissions
  pubreg
  status
  teams

Options:{BASE_COMMAND_OPTIONS}
"""
    log = logging.getLogger(__name__)
    sub_commands = []
    args: dict

    def __init__(self, sdk=SDK):
        self.args = docopt(str(self.__doc__))
        self.sdk = sdk(env=self.opt("env"))

        if self.opt("debug"):
            logging.basicConfig(level=logging.DEBUG)

    def handle(self):
        self.args = docopt(str(self.__doc__))
        for cmd in self.sub_commands:
            try:
                self.log.debug(f"Checking if sub_command '{cmd.__name__}' is valid")
                return cmd(self.sdk.__class__).handle()
            except DocoptExit as d:
                self.log.debug(d.usage)
        return self.handler()

    def handler(self):
        raise NotImplementedError("Missing handler")

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

    def confirm_to_continue(self, message):
        """Ask the user for confirmation before continuing.

        Any answer other than "y" will exit the program.
        """
        self.print(message)
        if input("Continue? [y/N]: ") != "y":
            self.print("Abort.")
            sys.exit()

    def login(self):
        self.sdk.login()

    @staticmethod
    def pretty_json(data):
        print(json.dumps(data, indent=2))

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
        if not isinstance(response_body, dict):
            print(response_body)
            return

        response_body.update({"error": 1})

        if self.opt("format") == "json":
            print(json.dumps(response_body))
        else:
            try:
                print(
                    _format_error_message(
                        response_body["message"], response_body.get("errors")
                    )
                )
            except KeyError:
                self.log.debug("Got unexpected response body from api.")
                print(response_body)


def _format_error_message(message, errors=None):
    msg = f"An error occurred: {message}"
    sep = "\n - "

    if isinstance(errors, list):
        msg += "\nCause{}:{}{}".format(
            "s" if len(errors) > 1 else "",
            sep,
            sep.join(
                err.get("msg", "") if isinstance(err, dict) else err for err in errors
            ),
        )
    elif errors:
        msg += f"\nCause:{sep}{errors}"

    return msg
