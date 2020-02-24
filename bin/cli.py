import sys
from requests.exceptions import HTTPError

from origo.exceptions import ApiAuthenticateError

from origocli.command import BaseCommand
from origocli.commands.datasets import DatasetsCommand
from origocli.commands.event_streams import EventStreamCommand
from origocli.commands.events import EventsCommand
from origocli.commands.pipelines import Pipelines


def main():
    argv = sys.argv
    if len(argv) < 2 or argv[1] == "help":
        BaseCommand().help()
        return

    command = get_command_class(argv)

    if command:
        instance = command()
        try:
            instance.sdk.login()
            return instance.handle()
        except HTTPError as he:
            instance.print_error_response(he.response.json())
        except ApiAuthenticateError:
            instance.print("Invalid credentials")
        except Exception as e:
            instance.log.exception(f"Failed badly: {e}")

    else:
        BaseCommand().help()


def get_command_class(argv):
    commands = {
        "datasets": DatasetsCommand,
        "events": EventsCommand,
        "pipelines": Pipelines,
        "event_streams": EventStreamCommand,
    }
    if argv[1] in commands:
        return commands[argv[1]]
    return False


if __name__ == "__main__":
    main()
