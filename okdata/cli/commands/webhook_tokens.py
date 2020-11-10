from origocli.command import BaseCommand, BASE_COMMAND_OPTIONS
from origocli.output import create_output

from origo.dataset_authorizer.simple_dataset_authorizer_client import (
    SimpleDatasetAuthorizerClient,
)


class WebhookTokensCommand(BaseCommand):
    __doc__ = f"""Oslo :: Webhook tokens

Usage:
  origo webhooks create-token <datasetid> <service> [options]
  origo webhooks delete-token <datasetid> <token> [options]
  origo webhooks list-tokens <datasetid> [options]

Examples:
  origo webhooks create-token some-dataset-id some-service-name --format=json
  origo webhooks delete-token some-dataset-id some-webhook-token
  origo webhooks list-tokens some-dataset-id

Options:{BASE_COMMAND_OPTIONS}
    """

    def __init__(self):
        super().__init__()
        env = self.opt("env")
        self.sdk = SimpleDatasetAuthorizerClient(env=env)
        self.handler = self.default

    def default(self):
        if self.cmd("create-token"):
            self.create_token()
        elif self.cmd("delete-token"):
            self.delete_token()
        elif self.cmd("list-tokens"):
            self.list_tokens()
        else:
            self.print("Invalid command")

    def create_token(self):
        out = create_output(self.opt("format"), "webhooks_token_config.json")
        out.output_singular_object = True
        dataset_id = self.arg("datasetid")
        service = self.arg("service")
        resp = self.sdk.create_webhook_token(dataset_id, service)
        out.add_row(resp)
        self.print("Creating webhook token", out)

    def delete_token(self):
        out = create_output(self.opt("format"), "webhooks_token_delete_config.json")
        out.output_singular_object = True
        dataset_id = self.arg("datasetid")
        webhook_token = self.arg("token")
        resp = self.sdk.delete_webhook_token(dataset_id, webhook_token)
        data = {
            "dataset_id": dataset_id,
            "webhook_token": webhook_token,
            "status": resp["message"],
        }
        out.add_row(data)
        self.print("Deleting webhook token", out)

    def list_tokens(self):
        out = create_output(self.opt("format"), "webhook_token_list_config.json")
        dataset_id = self.arg("datasetid")
        webhook_tokens = self.sdk.list_webhook_tokens(dataset_id)
        out.add_rows(webhook_tokens)
        self.print(f"Webhook tokens registered on dataset {dataset_id}: ", out)
