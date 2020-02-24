from conftest import set_argv
import pytest

from origocli.commands.event_streams import EventStreamCommand
from origo.event.event_stream_client import EventStreamClient


def test_create(mock_event_stream_sdk, mocker):
    set_argv("event_streams", "create", "some-dataset-id", "1")
    cmd = EventStreamCommand()
    mocker.spy(cmd.sdk, "create_event_stream")
    cmd.handler()
    cmd.sdk.create_event_stream.assert_called_once_with("some-dataset-id", "1")


def test_ls(mock_event_stream_sdk, mocker):
    set_argv("event_streams", "ls", "some-dataset-id", "1")
    cmd = EventStreamCommand()
    mocker.spy(cmd.sdk, "get_event_stream_info")
    cmd.handler()
    cmd.sdk.get_event_stream_info.assert_called_once_with("some-dataset-id", "1")


def test_delete(mock_event_stream_sdk, mocker):
    set_argv("event_streams", "delete", "some-dataset-id", "1")
    cmd = EventStreamCommand()
    mocker.spy(cmd.sdk, "delete_event_stream")
    cmd.handler()
    cmd.sdk.delete_event_stream.assert_called_once_with("some-dataset-id", "1")


@pytest.fixture()
def mock_event_stream_sdk(monkeypatch):
    def create_event_stream_return(self, dataset_id, version):
        return {"message": "Ok"}

    def get_event_stream_info(self, dataset_id, version):
        return {"message": "Ok"}

    def delete_event_stream(self, dataset_id, version):
        return {"message": "Ok"}

    monkeypatch.setattr(
        EventStreamClient, "create_event_stream", create_event_stream_return
    )
    monkeypatch.setattr(
        EventStreamClient, "get_event_stream_info", get_event_stream_info
    )
    monkeypatch.setattr(EventStreamClient, "delete_event_stream", delete_event_stream)
