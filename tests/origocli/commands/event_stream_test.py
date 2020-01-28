from conftest import set_argv

from origocli.commands.event_streams import EventStreamCommand


def test_create(mocker):
    set_argv("event_streams", "create", "some-dataset-id", "1")
    cmd = EventStreamCommand()
    mocker.spy(cmd.sdk, "create_event_stream")
    cmd.handler()
    cmd.sdk.create_event_stream.assert_called_once_with("some-dataset-id", "1")


def test_ls(mocker):
    set_argv("event_streams", "ls", "some-dataset-id", "1")
    cmd = EventStreamCommand()
    mocker.spy(cmd.sdk, "get_event_stream_info")
    cmd.handler()
    cmd.sdk.get_event_stream_info.assert_called_once_with("some-dataset-id", "1")


def test_delete(mocker):
    set_argv("event_streams", "delete", "some-dataset-id", "1")
    cmd = EventStreamCommand()
    mocker.spy(cmd.sdk, "delete_event_stream")
    cmd.handler()
    cmd.sdk.delete_event_stream.assert_called_once_with("some-dataset-id", "1")
