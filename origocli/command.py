import json
import logging
import sys

from pygments import highlight, lexers, formatters


class BaseCommand:
    log = logging.getLogger(__name__)
    sub_commands = None
    args: dict
    handler: ()

    def __init__(self, args):
        self.args = args
        if self.opt("debug"):
            logging.basicConfig(level=logging.DEBUG)

    def __call__(self):
        if self.sub_commands:
            command = self.current_command()
            if command in self.sub_commands:
                return self.sub_commands[command]

        if not hasattr(self, "handler"):
            self.log.info("command was implemented without a default handler")
            print(self.__doc__, end="")
        else:
            self.handler()

        return None

    def current_command(self):
        return self.arg("command")

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
