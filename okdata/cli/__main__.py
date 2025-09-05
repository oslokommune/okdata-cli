import json
import os
import sys

from keycloak.exceptions import KeycloakGetError, KeycloakPostError
from okdata.sdk.exceptions import ApiAuthenticateError
from requests.exceptions import RequestException

from okdata.cli import MAINTAINER
from okdata.cli.command import BaseCommand
from okdata.cli.commands.datasets import DatasetsCommand
from okdata.cli.commands.permissions import PermissionsCommand
from okdata.cli.commands.pubs import PubsCommand
from okdata.cli.commands.status import StatusCommand
from okdata.cli.commands.teams.teams import TeamsCommand


def main():
    argv = sys.argv
    if len(argv) < 2:
        BaseCommand().help()
        return
    if argv[1] in ("-e", "--environment"):
        BaseCommand().print_env()
        return
    if argv[1] in ("-v", "--version"):
        BaseCommand().print_version()
        return

    command = get_command_class(argv)

    if command:
        instance = command()
        try:
            instance.login()
            instance.handle()
            # Flush output here to force SIGPIPE to be triggered while inside
            # this try block.
            sys.stdout.flush()
        except RequestException as e:
            if hasattr(e.response, "json"):
                instance.print_error_response(e.response.json())
            else:
                instance.print(
                    "A server error occurred. Please try again, or contact "
                    f"{MAINTAINER} if the problem persists.",
                )
        except ApiAuthenticateError:
            instance.print(
                "An error occurred (ApiAuthenticateError): Invalid credentials",
                {"error": 1, "message": "Invalid credentials"},
            )
        except (KeycloakGetError, KeycloakPostError) as e:
            error = json.loads(e.error_message)
            error_type = e.__class__.__name__
            instance.log.info(f"Keycloak reported: {e}")
            instance.print(
                f"An error occurred ({error_type}): {error['error_description']}"
            )
        except (EOFError, KeyboardInterrupt):
            instance.print("\nAbort.")
        except BrokenPipeError:
            # https://docs.python.org/3/library/signal.html#note-on-sigpipe
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
            sys.exit(1)
        except Exception as e:
            instance.print(
                "An exception occurred",
                {
                    "error": 1,
                    "message": (
                        "okdata-cli failed with an exception, see log output "
                        "for more information",
                    ),
                },
            )
            instance.log.exception(f"okdata-cli failed with: {e}")

    else:
        BaseCommand().help()


def get_command_class(argv):
    commands = {
        "datasets": DatasetsCommand,
        "permissions": PermissionsCommand,
        "pubs": PubsCommand,
        "status": StatusCommand,
        "teams": TeamsCommand,
    }
    return commands.get(argv[1], False)


if __name__ == "__main__":
    main()
