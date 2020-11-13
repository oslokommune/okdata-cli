from conftest import set_argv
import pytest

from okdata.cli.commands.datasets import DatasetsCommand
from okdata.sdk.dataset_authorizer.simple_dataset_authorizer_client import (
    SimpleDatasetAuthorizerClient,
)


dataset_id = "some-dataset-id"
principal_id = "some-user-name"


def test_create_access(mock_simple_dataset_auth_sdk, mocker):
    set_argv("datasets", "create-access", dataset_id, principal_id)
    cmd = DatasetsCommand()
    mocker.spy(cmd.simple_dataset_auth_sdk, "create_dataset_access")
    cmd.handler()
    cmd.simple_dataset_auth_sdk.create_dataset_access.assert_called_once_with(
        dataset_id, principal_id
    )


def test_check_access(mock_simple_dataset_auth_sdk, mocker):
    set_argv("datasets", "check-access", dataset_id)
    cmd = DatasetsCommand()
    mocker.spy(cmd.simple_dataset_auth_sdk, "check_dataset_access")
    cmd.handler()
    cmd.simple_dataset_auth_sdk.check_dataset_access.assert_called_once_with(dataset_id)


@pytest.fixture()
def mock_simple_dataset_auth_sdk(monkeypatch):
    def create_dataset_access_return(self, dataset_id, principal_id):
        return {"message": "Created"}

    def check_dataset_access_return(self, dataset_id):
        return {"access": True}

    monkeypatch.setattr(
        SimpleDatasetAuthorizerClient,
        "create_dataset_access",
        create_dataset_access_return,
    )

    monkeypatch.setattr(
        SimpleDatasetAuthorizerClient,
        "check_dataset_access",
        check_dataset_access_return,
    )
