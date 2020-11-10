from conftest import set_argv
import pytest

from origocli.commands.webhook_tokens import WebhookTokensCommand
from okdata.sdk.dataset_authorizer.simple_dataset_authorizer_client import (
    SimpleDatasetAuthorizerClient,
)


dataset_id = "some-dataset-id"
service_name = "some-service-name"
webhook_token = "27580f43-7674-4033-87e2-285db632903d"


def test_create(mock_simple_dataset_auth_sdk, mocker):
    set_argv("webhooks", "create-token", dataset_id, service_name)
    cmd = WebhookTokensCommand()
    mocker.spy(cmd.sdk, "create_webhook_token")
    cmd.handler()
    cmd.sdk.create_webhook_token.assert_called_once_with(dataset_id, service_name)


def test_delete(mock_simple_dataset_auth_sdk, mocker):
    set_argv("webhooks", "delete-token", dataset_id, webhook_token)
    cmd = WebhookTokensCommand()
    mocker.spy(cmd.sdk, "delete_webhook_token")
    cmd.handler()
    cmd.sdk.delete_webhook_token.assert_called_once_with(dataset_id, webhook_token)


def test_list_webhook_tokens(mock_simple_dataset_auth_sdk, mocker):
    set_argv("webhooks", "list-tokens", dataset_id)
    cmd = WebhookTokensCommand()
    mocker.spy(cmd.sdk, "list_webhook_tokens")
    cmd.handler()
    cmd.sdk.list_webhook_tokens.assert_called_once_with(dataset_id)


@pytest.fixture()
def mock_simple_dataset_auth_sdk(monkeypatch):
    def create_webhook_token_return(self, dataset_id, version):
        return {"token": webhook_token}

    def delete_webhook_token_return(self, dataset_id, token):
        return {"message": "Deleted"}

    def list_webhook_tokens_return(self, dataset_id):
        return [
            {
                "token": "7271646a-8530-4ed3-a042-4485fbbd7460",
                "created_by": "janedoe",
                "dataset_id": "some-dataset",
                "service": "service-account-some-service",
                "created_at": "2020-07-09T06:57:36+00:00",
                "expires_at": "2022-07-09T06:57:36+00:00",
                "is_active": True,
            }
        ]

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

    monkeypatch.setattr(
        SimpleDatasetAuthorizerClient,
        "list_webhook_tokens",
        list_webhook_tokens_return,
    )
