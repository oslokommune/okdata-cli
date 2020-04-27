from origocli.command import BaseCommand

from origo.dataset_authorizer.simple_dataset_authorizer_client import (
    SimpleDatasetAuthorizerClient,
)


class WebhookTokensCommand(BaseCommand):
    """Oslo :: Webhook tokens

    Usage:
      origo webhook_tokens create <datasetid> <service> [--format=<format> options]
      origo webhook_tokens delete <datasetid> <token> [--format=<format> options]

    Options:
      -d --debug
      -h --help
    """

    def __init__(self):
        super().__init__()
        env = self.opt("env")
        self.sdk = SimpleDatasetAuthorizerClient(env=env)
        self.handler = self.default

    def default(self):
        if self.cmd("create"):
            self.create()
        elif self.cmd("delete"):
            self.delete()
        else:
            self.print("Invalid command")

    def create(self):
        dataset_id = self.arg("datasetid")
        service = self.arg("service")
        response = self.sdk.create_webhook_token(dataset_id, service)
        token = response["token"]
        self.print(
            f"Webhook token created for service {service} on dataset {dataset_id}: {token}",
            response,
        )

    def delete(self):
        dataset_id = self.arg("datasetid")
        token = self.arg("token")
        response = self.sdk.delete_webhook_token(dataset_id, token)
        self.print(response["message"], response)
