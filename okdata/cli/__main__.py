import json
import sys

from keycloak.exceptions import KeycloakGetError
from okdata.sdk.exceptions import ApiAuthenticateError
from requests.exceptions import RequestException

from okdata.cli import MAINTAINER
from okdata.cli.command import BaseCommand
from okdata.cli.commands.datasets import DatasetsCommand
from okdata.cli.commands.permissions import PermissionsCommand
from okdata.cli.commands.pubreg import PubregCommand
from okdata.cli.commands.status import StatusCommand
from okdata.cli.commands.teams.teams import TeamsCommand


def main():
    argv = sys.argv
    if len(argv) < 2 or argv[1] == "help":
        BaseCommand().help()
        return

    command = get_command_class(argv)

    if command:
        instance = command()
        try:
            instance.login()
            instance.handle()
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
        except KeycloakGetError as e:
            error = json.loads(e.error_message)
            instance.log.info(f"Keycloak reported: {e}")
            instance.print(
                f"An error occurred (KeycloakGetError): {error['error_description']}"
            )
        except (EOFError, KeyboardInterrupt):
            instance.print("\nAbort.")
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
        "pubreg": PubregCommand,
        "status": StatusCommand,
        "teams": TeamsCommand,
    }
    return commands.get(argv[1], False)


if __name__ == "__main__":
    main()
