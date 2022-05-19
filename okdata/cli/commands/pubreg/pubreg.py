import base64
from operator import itemgetter

from okdata.sdk.team.client import TeamClient
from requests.exceptions import HTTPError

from okdata.cli.command import BASE_COMMAND_OPTIONS, BaseCommand
from okdata.cli.commands.pubreg.client import PubregClient
from okdata.cli.commands.pubreg.wizards import (
    CreateClientWizard,
    CreateKeyWizard,
    NoClientsError,
)
from okdata.cli.output import create_output


class PubregCommand(BaseCommand):
    __doc__ = f"""Oslo :: Public registers

Usage:
  okdata pubreg create-client [options]
  okdata pubreg list-clients (test|prod) [options]
  okdata pubreg delete-client (test|prod) <client-id> [options]
  okdata pubreg create-key [options]
  okdata pubreg list-keys (test|prod) <client-id> [options]
  okdata pubreg delete-key (test|prod) <client-id> <key-id> [options]

Examples:
  okdata pubreg create-client
  okdata pubreg list-clients test
  okdata pubreg delete-client test my-client
  okdata pubreg create-key
  okdata pubreg list-keys test my-client
  okdata pubreg delete-key test my-client 2020-01-01-12-00-00

Options:{BASE_COMMAND_OPTIONS}
    """

    def __init__(self):
        super().__init__()
        self.client = PubregClient(env=self.opt("env"))

    def handler(self):
        maskinporten_env = "prod" if self.cmd("prod") else "test"

        if self.cmd("create-client"):
            self.create_client()
        elif self.cmd("list-clients"):
            self.list_clients(maskinporten_env)
        elif self.cmd("delete-client"):
            self.delete_client(
                maskinporten_env,
                self.arg("client-id"),
            )
        elif self.cmd("create-key"):
            self.create_client_key()
        elif self.cmd("list-keys"):
            self.list_client_keys(
                maskinporten_env,
                self.arg("client-id"),
            )
        elif self.cmd("delete-key"):
            self.delete_client_key(
                maskinporten_env,
                self.arg("client-id"),
                self.arg("key-id"),
            )

    def create_client(self):
        team_client = TeamClient(env=self.opt("env"))
        teams = team_client.get_teams(has_role="origo-team")

        if not teams:
            self.print(
                "We haven't yet registered you as member of any Origo team. "
                "Please contact Datapatruljen to get it done."
            )
            return

        config = CreateClientWizard(teams).start()

        team_id = config["team_id"]
        provider_id = config["provider_id"]
        provider_name = config["provider_name"]
        integration = config["integration"]
        scopes = config["scopes"]
        env = config["env"]

        self.confirm_to_continue(
            f"Will create a new client for {provider_name} in {env} with "
            f"scopes {scopes}."
        )

        try:
            self.print("Creating client...")
            response = self.client.create_client(
                team_id, provider_id, integration, scopes, env
            )
            client_id = response["client_id"]
            self.print(
                f"""
Done! Created a new client with ID '{client_id}'.
You may now go ahead and create a key for it by running:

  okdata pubreg create-key"""
            )
        except HTTPError as e:
            message = e.response.json()["message"]
            self.print(f"Something went wrong: {message}")

    def list_clients(self, env):
        clients = self.client.get_clients(env)
        out = create_output(self.opt("format"), "pubreg_clients_config.json")
        out.add_rows(sorted(clients, key=itemgetter("client_name")))
        self.print(f"Clients in ({env}):", out)

    def delete_client(self, env, client_id):
        try:
            self.print(f"Deleting client '{client_id}' ({env})...")
            self.client.delete_client(env, client_id)
            self.print("Done! The client is deleted and will no longer work.")
        except HTTPError as e:
            message = e.response.json()["message"]
            self.print(f"Something went wrong: {message}")

    def _handle_new_key_aws(self, key):
        params = key.get("ssm_params")

        if params:
            self.print(
                "The following {} been written to SSM:".format(
                    "parameter has" if len(params) == 1 else "parameters have"
                )
            )
            for param in params:
                self.print(f"- {param}")
        else:
            self.print(
                "The key was created, but it appears that the relevant "
                "parameters weren't added to SSM. This should not happen, "
                "please contact Datapatruljen!"
            )

    def _handle_new_key_local(self, key, client_name, env):
        outfile = f"{client_name}-{env}-{key['kid']}.p12"

        with open(outfile, "wb") as f:
            f.write(base64.b64decode(key["keystore"]))

        self.print(f"Key ID:   {key['kid']}")
        self.print(f"Key file: {outfile}")
        self.print(f"Password: {key['key_password']}\n")

        self.print(
            "The password can't be retrieved again later, so be sure to save it."
        )

    def create_client_key(self):
        self.confirm_to_continue(
            "WARNING: Due to how Maskinporten works, the expiration date of "
            "every existing key will be updated to today's date when creating "
            "a new key.\n  (Digdir is looking into a fix for this issue.)"
        )

        try:
            config = CreateKeyWizard(self.client).start()
        except NoClientsError:
            self.print(
                "No clients in the given environment yet!\n\n"
                "  Create one with `okdata pubreg create-client`.\n"
            )
            return

        env = config["env"]
        client_id = config["client_id"]
        client_name = config["client_name"]
        aws_account = config["aws_account"]
        aws_region = config["aws_region"]

        self.confirm_to_continue(
            "Will create a new key for client '{}' in {}{}.".format(
                client_name,
                env,
                f", and send it to AWS account {aws_account} ({aws_region})"
                if aws_account and aws_region
                else "",
            )
        )

        self.print("Creating key for '{}' ({})...".format(client_name, env))

        try:
            key = self.client.create_key(
                env,
                client_id,
                aws_account,
                aws_region,
            )
        except HTTPError as e:
            message = e.response.json()["message"]
            self.print(f"Something went wrong: {message}")
            return

        self.print(
            "\nA new key has been created and stored in the current working "
            "directory.\n"
        )

        if key.get("ssm_params") is not None:
            self._handle_new_key_aws(key)
        elif key.get("keystore") and key.get("key_password"):
            self._handle_new_key_local(key, client_name, env)
        else:
            self.print(
                "The key was neither added to AWS nor returned to the "
                "client. This should not happen, please contact "
                "Datapatruljen!"
            )

    def list_client_keys(self, env, client_id):
        keys = self.client.get_keys(env, client_id)
        out = create_output(self.opt("format"), "pubreg_client_keys_config.json")
        out.add_rows(sorted(keys, key=itemgetter("kid")))
        self.print(f"Keys for client {client_id} ({env}):", out)

    def delete_client_key(self, env, client_id, key_id):
        self.confirm_to_continue(
            "WARNING: Due to how Maskinporten works, the expiration dates of "
            "all other keys will be updated to today's date when deleting "
            "a key.\n  (Digdir is looking into a fix for this issue.)"
        )

        try:
            self.print(
                f"Deleting key '{key_id}' from '{client_id}' ({env})...",
            )
            self.client.delete_key(env, client_id, key_id)
            self.print("Done! The key is deleted and will no longer work.")
        except HTTPError as e:
            message = e.response.json()["message"]
            self.print(f"Something went wrong: {message}")
