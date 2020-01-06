import json
import logging
import os
import sys
from typing import Type

from docopt import docopt
from origo.pipelines import resources
from origo.pipelines.resources.pipeline_base import PipelineBase
from origo.sdk import SDK
from pygments import highlight, lexers, formatters

from origocli.output import TableOutput


class BaseCommand:
    """
    usage:
      origo [command] [options]

    Commands available:
      datasets
      events
      pipeline
      help

    options:
      -d --debug
    """
    log = logging.getLogger(__name__)
    sub_commands = None
    args: dict
    handler: ()
    sdk = SDK()

    def handle(self):
        self.args = docopt(str(self.__doc__))
        if self.sub_commands:
            for cmd in self.sub_commands:
                if self.cmd(cmd):
                    return self.sub_commands[cmd](self.sdk).handle()
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
        colorful_json = highlight(output, lexers.JsonLexer(), formatters.TerminalFormatter())
        print(colorful_json)

    def print_success(self, resource: Type[PipelineBase], data):
        def _for(properties):
            for property in properties:
                body = properties[property]
                if "properties" not in body:
                    yield body["title"], {
                        "name": body["title"],
                        "key": property
                    }
                else:
                    _for(body["properties"])

        with open(os.path.dirname(resources.__file__) + f"/schemas/{resource.__resource_name__}.json", "r") as f:
            schema = json.loads(f.read())
            config = {key: body for key, body in _for(schema["properties"])}

            config.pop("The Template Schema", None)
            config.pop("The Transformation_schema Schema", None)
            config.pop("The Transformation Schema", None)
        table = TableOutput(config)
        for row in data:
            table.add_row(row)
        print(table)

    def no_data(self, str):
        if self.opt("format") == "json":
            print(f"{str}")
