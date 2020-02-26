from conftest import set_argv
import pytest
from origocli.commands.status import StatusCommand
from origo.status import Status


def test_get_status(mock_status_sdk, mocker):
    set_argv("status", "my-uu-ii-dd")
    cmd = StatusCommand()
    mocker.spy(cmd.sdk, "get_status")
    mocker.spy(cmd, "add_status_for_id_rows")
    cmd.handler()
    cmd.sdk.get_status.assert_called_once_with("my-uu-ii-dd")
    cmd.add_status_for_id_rows.assert_called_once()


def test_get_status_with_history(mock_status_sdk, mocker):
    set_argv("status", "my-uu-ii-dd", "--history")
    cmd = StatusCommand()
    mocker.spy(cmd.sdk, "get_status")
    mocker.spy(cmd, "full_history_for_status")
    cmd.handler()
    cmd.sdk.get_status.assert_called_once_with("my-uu-ii-dd")
    cmd.full_history_for_status.assert_called_once()


@pytest.fixture()
def mock_status_sdk(monkeypatch):
    def get_status_return(self, uuid):
        return [{"id": "my-uu-ii-dd", "run_status": "FINISHED", "status": "OK"}]

    monkeypatch.setattr(Status, "get_status", get_status_return)
