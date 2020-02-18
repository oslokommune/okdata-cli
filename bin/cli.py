import sys
from docopt import docopt

from origocli.command import BaseCommand
from origocli.commands.datasets import DatasetsCommand
from origocli.commands.event_streams import EventStreamCommand
from origocli.commands.events import EventsRegistry
from origocli.commands.pipelines import Pipelines


def main():
    argv = sys.argv
    if len(argv) < 2 or argv[1] == "help":
        BaseCommand().help()
        return False

    command = get_command_class(argv)

    if command is not False:
        instance = command()
        return instance.handle()
    BaseCommand().help()
    return False


def get_command_class(argv):
    commands = {
        "datasets": DatasetsCommand,
        "events": EventsRegistry,
        "pipelines": Pipelines,
        "event_streams": EventStreamCommand,
    }
    if argv[1] in commands:
        return commands[argv[1]]
    return False


class RootCommand(BaseCommand):
    """Oslo

Usage:
  origo [-d|--debug] [--format=<format>] <command> [<args>...]

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

    sub_commands = {
        "datasets": DatasetsCommand,
        "events": EventsRegistry,
        "pipelines": Pipelines,
        "event_stream": EventStreamCommand,
    }


if __name__ == "__main__":
    args = docopt(RootCommand.__doc__, options_first=True)
    argv = [args["<command>"]] + args["<args>"]
    root = RootCommand(args)
    CommandCls = root()

    while CommandCls:
        options_first = CommandCls.sub_commands and True or False
        new_args = docopt(CommandCls.__doc__, options_first=options_first, argv=argv)
        args = {**args, **new_args}
        instance = CommandCls(args)
        CommandCls = instance()
