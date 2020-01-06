import sys

from origocli.command import Command
from origocli.commands.datasets import DatasetsCommand
from origocli.commands.events import EventsCommand
from origocli.commands.pipelines import PipelinesCommand, BaseCommand


def main():
    argv = sys.argv
    if len(argv) < 2 or argv[1] == "help":
        Command.help()
        return False

    command = get_command_class(argv)

    if command is not False:
        instance = command()
        return instance.handle()
    print(BaseCommand.__doc__)
    return False


def get_command_class(argv):
    commands = {
        "datasets": DatasetsCommand,
        "events": EventsCommand,
        "pipelines": PipelinesCommand
    }
    if argv[1] in commands:
        return commands[argv[1]]
    return False
