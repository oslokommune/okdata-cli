from conftest import set_argv
import pytest

from origocli.commands.webhook_tokens import WebhookTokensCommand
from origo.dataset_authorizer.simple_dataset_authorizer_client import (
    SimpleDatasetAuthorizerClient,
)


dataset_id = "some-dataset-id"
service_name = "some-service-name"
webhook_token = "27580f43-7674-4033-87e2-285db632903d"


def test_create(mock_simple_dataset_auth_sdk, mocker):
    set_argv("webhook_tokens", "create", dataset_id, service_name)
    cmd = WebhookTokensCommand()
    mocker.spy(cmd.sdk, "create_webhook_token")
    cmd.handler()
    cmd.sdk.create_webhook_token.assert_called_once_with(dataset_id, service_name)


def test_delete(mock_simple_dataset_auth_sdk, mocker):
    set_argv("webhook_tokens", "delete", dataset_id, webhook_token)
    cmd = WebhookTokensCommand()
    mocker.spy(cmd.sdk, "delete_webhook_token")
    cmd.handler()
    cmd.sdk.delete_webhook_token.assert_called_once_with(dataset_id, webhook_token)


@pytest.fixture()
def mock_simple_dataset_auth_sdk(monkeypatch):
    def create_webhook_token_return(self, dataset_id, version):
        return {"token": webhook_token}

    def delete_webhook_token_return(self, dataset_id, token):
        return {"message": "Deleted"}

    monkeypatch.setattr(
        SimpleDatasetAuthorizerClient,
        "create_webhook_token",
        create_webhook_token_return,
    )

    monkeypatch.setattr(
        SimpleDatasetAuthorizerClient,
        "delete_webhook_token",
        delete_webhook_token_return,
    )
