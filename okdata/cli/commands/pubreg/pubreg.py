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
  okdata pubreg create-client [--env=<env>]
  okdata pubreg list-keys <maskinporten-env> <client-id> [--env=<env>]

Examples:
  okdata pubreg create-client
  okdata pubreg list-keys test my-client

Options:{BASE_COMMAND_OPTIONS}
    """

    def __init__(self):
        super().__init__()
        self.client = PubregClient(env=self.opt("env"))

    def handler(self):
        if self.cmd("create-client"):
            self.create_client()
        if self.cmd("list-keys"):
            self.list_client_keys(self.arg("maskinporten-env"), self.arg("client-id"))

    def create_client(self):
        config = ClientCreateWizard().start()

        team = config["team"]
        provider = config["provider"]
        env = config["environment"]
        scopes = config["scopes"]

        name = f"{team}-{provider}-{env}-{uuid.uuid4()}"

        self.print(f"Will create a new client '{name}' in {env} with scopes {scopes}.")
        if input("Continue? [y/N]: ") != "y":
            self.print("Aborted")
            return

        try:
            self.print("Creating '{name}'...")
            self.client.create_client(env, name, scopes)
            self.print("Done!")
        except HTTPError as e:
            self.print(f"Something went wrong: {e}")

    def list_client_keys(self, env, client_id):
        keys = self.client.get_keys(env, client_id)
        out = create_output(self.opt("format"), "pubreg_client_keys_config.json")
        out.add_rows(sorted(keys, key=itemgetter("kid")))
        self.print(f"Keys for client {client_id} ({env}):", out)
