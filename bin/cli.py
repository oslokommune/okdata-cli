import json
import sys

from requests.exceptions import HTTPError
from keycloak.exceptions import KeycloakGetError

from origo.exceptions import ApiAuthenticateError

from origocli.command import BaseCommand
from origocli.commands.datasets import DatasetsCommand
from origocli.commands.event_streams import EventStreamCommand
from origocli.commands.events import EventsCommand
from origocli.commands.pipelines import Pipelines
from origocli.commands.status import StatusCommand
from origocli.commands.webhook_tokens import WebhookTokensCommand


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
        except HTTPError as he:
            instance.print_error_response(he.response.json())
        except ApiAuthenticateError:
            instance.print(
                "An error occured (ApiAuthenticateError): Invalid credentials",
                {"error": 1, "message": "Invalid credentials"},
            )
        except KeycloakGetError as e:
            error = json.loads(e.error_message)
            instance.log.info(f"Keycloak reported: {e}")
            instance.print(
                f"An error occured (KeycloakGetError): {error['error_description']}"
            )
        except Exception as e:
            instance.print(
                "A Exception occured",
                {
                    "error": 1,
                    "message": "Origo CLI failed with exception, see log output for more information",
                },
            )
            instance.log.exception(f"Origo CLI failed with: {e}")

    else:
        BaseCommand().help()


def get_command_class(argv):
    commands = {
        "datasets": DatasetsCommand,
        "events": EventsCommand,
        "pipelines": Pipelines,
        "event_streams": EventStreamCommand,
        "status": StatusCommand,
        "webhooks": WebhookTokensCommand,
    }
    if argv[1] in commands:
        return commands[argv[1]]
    return False


if __name__ == "__main__":
    main()
