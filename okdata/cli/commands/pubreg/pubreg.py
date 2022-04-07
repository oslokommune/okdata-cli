import uuid
from operator import itemgetter

from requests.exceptions import HTTPError

from okdata.cli.command import BASE_COMMAND_OPTIONS, BaseCommand
from okdata.cli.commands.pubreg.client import PubregClient
from okdata.cli.commands.pubreg.wizards import ClientCreateWizard
from okdata.cli.output import create_output


class PubregCommand(BaseCommand):
    __doc__ = f"""Oslo :: Public registers

Usage:
  okdata pubreg create-client [options]
  okdata pubreg list-clients <maskinporten-env> [options]
  okdata pubreg create-key <maskinporten-env> <client-id> <aws-account> <aws-region> [options]
  okdata pubreg list-keys <maskinporten-env> <client-id> [options]

Examples:
  okdata pubreg create-client
  okdata pubreg list-clients test
  okdata pubreg create-key test my-client 123456789101 eu-west-1
  okdata pubreg list-keys test my-client

Options:{BASE_COMMAND_OPTIONS}
    """

    def __init__(self):
        super().__init__()
        self.client = PubregClient(env=self.opt("env"))

    def handler(self):
        if self.cmd("create-client"):
            self.create_client()
        elif self.cmd("list-clients"):
            self.list_clients(self.arg("maskinporten-env"))
        elif self.cmd("create-key"):
            self.create_client_key(
                self.arg("maskinporten-env"),
                self.arg("client-id"),
                self.arg("aws-account"),
                self.arg("aws-region"),
            )
        elif self.cmd("list-keys"):
            self.list_client_keys(self.arg("maskinporten-env"), self.arg("client-id"))

    def create_client(self):
        config = ClientCreateWizard().start()

        team = config["team"]
        provider = config["provider"]
        env = config["environment"]
        scopes = config["scopes"]

        name = f"{team}-{provider}-{env}-{uuid.uuid4()}"

        self.confirm_to_continue(
            f"Will create a new client '{name}' in {env} with scopes {scopes}."
        )

        try:
            self.print(f"Creating '{name}'...")
            response = self.client.create_client(env, name, scopes)
            client_id = response["client_id"]
            self.print(f"Done! Created a new client with ID '{client_id}'.")
        except HTTPError as e:
            message = e.response.json()["message"]
            self.print(f"Something went wrong: {message}")

    def list_clients(self, env):
        clients = self.client.get_clients(env)
        out = create_output(self.opt("format"), "pubreg_clients_config.json")
        out.add_rows(sorted(clients, key=itemgetter("client_name")))
        self.print(f"Clients in ({env}):", out)

    def create_client_key(self, env, client_id, aws_account, aws_region):
        self.confirm_to_continue(
            "WARNING: Due to how Maskinporten works, the expiration date of "
            "every existing key will be updated to today's date when creating "
            "a new key.\n  (Digdir is looking into a fix for this issue.)"
        )

        try:
            self.print(f"Creating key for '{client_id}' ({env})...")
            self.client.create_key(env, client_id, aws_account, aws_region)
            self.print("Done!")
        except HTTPError as e:
            message = e.response.json()["message"]
            self.print(f"Something went wrong: {message}")

    def list_client_keys(self, env, client_id):
        keys = self.client.get_keys(env, client_id)
        out = create_output(self.opt("format"), "pubreg_client_keys_config.json")
        out.add_rows(sorted(keys, key=itemgetter("kid")))
        self.print(f"Keys for client {client_id} ({env}):", out)
