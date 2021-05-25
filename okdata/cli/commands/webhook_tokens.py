from okdata.sdk.webhook.client import WebhookClient

from okdata.cli.command import BaseCommand, BASE_COMMAND_OPTIONS
from okdata.cli.output import create_output


class WebhookTokensCommand(BaseCommand):
    __doc__ = f"""Oslo :: Webhook tokens

Usage:
  okdata webhooks create-token <datasetid> <operation> [options]
  okdata webhooks delete-token <datasetid> <token> [options]
  okdata webhooks list-tokens <datasetid> [options]

Examples:
  okdata webhooks create-token my-dataset read
  okdata webhooks create-token my-dataset write
  okdata webhooks delete-token my-dataset 6fb92252-9390-802c-4218-ce7e1f934bf5
  okdata webhooks list-tokens my-dataset

Options:{BASE_COMMAND_OPTIONS}
    """

    def __init__(self):
        super().__init__()
        env = self.opt("env")
        self.sdk = WebhookClient(env=env)
        self.handler = self.default

    def default(self):
        dataset_id = self.arg("datasetid")

        if self.cmd("create-token"):
            self.create_token(dataset_id, self.arg("operation"))
        elif self.cmd("delete-token"):
            self.delete_token(dataset_id, self.arg("token"))
        elif self.cmd("list-tokens"):
            self.list_tokens(dataset_id)
        else:
            self.print("Invalid command")

    def create_token(self, dataset_id, operation):
        out = create_output(self.opt("format"), "webhooks_token_config.json")
        out.output_singular_object = True
        out.add_row(self.sdk.create_webhook_token(dataset_id, operation))
        self.print("Created webhook token:", out)

    def delete_token(self, dataset_id, webhook_token):
        out = create_output(self.opt("format"), "webhooks_token_delete_config.json")
        out.output_singular_object = True
        resp = self.sdk.delete_webhook_token(dataset_id, webhook_token)
        data = {
            "dataset_id": dataset_id,
            "webhook_token": webhook_token,
            "status": resp["message"],
        }
        out.add_row(data)
        self.print("Deleted webhook token:", out)

    def list_tokens(self, dataset_id):
        out = create_output(self.opt("format"), "webhook_token_list_config.json")
        out.add_rows(self.sdk.list_webhook_tokens(dataset_id))
        self.print(f"Webhook tokens registered on dataset {dataset_id}: ", out)
