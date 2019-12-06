import sys

from origocli.command import Command
from origocli.commands.datasets import DatasetsCommand
from origocli.commands.events import EventsCommand


def main():
    argv = sys.argv
    if len(argv) < 2 or argv[1] == "help":
        Command.help()
        return False

    command = get_command_class(argv)

    if command is not False:
        instance = command()
        return instance.handle()
    return False


def get_command_class(argv):
    commands = {"datasets": DatasetsCommand, "events": EventsCommand}
    if argv[1] in commands:
        return commands[argv[1]]
    return False
