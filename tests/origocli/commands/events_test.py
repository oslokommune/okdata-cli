import pytest
from conftest import set_argv
from origo.event.post_event import PostEvent
from origo.event.event_stream_client import EventStreamClient
from origocli.output import TableOutput
from origocli.commands.events import EventsCommand


pipeline_client_qual = f"{PostEvent.__module__}.{PostEvent.__name__}"

dataset_id = "test-dataset"
version = "1"
sink_id = "abc123"
event_stream_item = {
    "status": "ACTIVE",
    "updated_by": "knut",
    "updated_at": "2020-08-26T08:07:21.903672+00:00",
    "id": f"{dataset_id}/{version}",
    "create_raw": True,
    "deleted": False,
    "confidentiality": "yellow",
}
subscribable_item = {
    "status": "INACTIVE",
    "updated_by": "janedone",
    "updated_at": "2020-08-20T06:51:42.786699+00:00",
    "enabled": False,
}
sink_item = {
    "id": sink_id,
    "type": "s3",
    "status": "ACTIVE",
    "updated_by": "janedone",
    "updated_at": "2020-08-20T06:51:42.786699+00:00",
}
sink_deleted_response = {
    "message": f"Deleted sink {sink_id} from stream {dataset_id}/{version}"
}


def output_with_argument(output, argument):
    for (args, kwargs) in output.call_args_list:
        if argument in args:
            return True
    return False


def test_ls_stream(mock_event_stream_sdk, mocker, mock_print):
    set_argv("events", "ls", f"ds:{dataset_id}/{version}")
    add_row = mocker.spy(TableOutput, "add_row")
    add_rows = mocker.spy(TableOutput, "add_rows")
    cmd = EventsCommand()
    mocker.spy(cmd.sdk, "get_event_stream_info")
    mocker.spy(cmd.sdk, "get_subscribable")
    mocker.spy(cmd.sdk, "get_sinks")
    cmd.handler()
    cmd.sdk.get_event_stream_info.assert_called_once_with(dataset_id, version)
    cmd.sdk.get_subscribable.assert_called_once_with(dataset_id, version)
    cmd.sdk.get_sinks.assert_called_once_with(dataset_id, version)
    assert output_with_argument(add_row, event_stream_item)
    assert output_with_argument(add_row, subscribable_item)
    assert output_with_argument(add_rows, [sink_item])
    assert mock_print.call_count == 3


def test_create_stream(mock_event_stream_sdk, mocker, mock_print):
    set_argv("events", "create-stream", f"ds:{dataset_id}/{version}", "--skip-raw")
    add_row = mocker.spy(TableOutput, "add_row")
    cmd = EventsCommand()
    mocker.spy(cmd.sdk, "create_event_stream")
    cmd.handler()
    cmd.sdk.create_event_stream.assert_called_once_with(
        dataset_id, version, create_raw=False
    )
    assert output_with_argument(add_row, event_stream_item)
    mock_print.assert_called_once()


def test_delete_stream(mock_event_stream_sdk, mocker, mock_print):
    set_argv("events", "delete-stream", f"ds:{dataset_id}/{version}")
    add_row = mocker.spy(TableOutput, "add_row")
    cmd = EventsCommand()
    mocker.spy(cmd.sdk, "delete_event_stream")
    cmd.handler()
    cmd.sdk.delete_event_stream.assert_called_once_with(dataset_id, version)
    assert output_with_argument(add_row, event_stream_item)
    mock_print.assert_called_once()


def test_enable_subscribable(mock_event_stream_sdk, mocker, mock_print):
    set_argv("events", "enable-subscribable", f"ds:{dataset_id}/{version}")
    add_row = mocker.spy(TableOutput, "add_row")
    cmd = EventsCommand()
    mocker.spy(cmd.sdk, "enable_subscribable")
    cmd.handler()
    cmd.sdk.enable_subscribable.assert_called_once_with(dataset_id, version)
    assert output_with_argument(add_row, subscribable_item)
    mock_print.assert_called_once()


def test_disable_subscribable(mock_event_stream_sdk, mocker, mock_print):
    set_argv("events", "disable-subscribable", f"ds:{dataset_id}/{version}")
    add_row = mocker.spy(TableOutput, "add_row")
    cmd = EventsCommand()
    mocker.spy(cmd.sdk, "disable_subscribable")
    cmd.handler()
    cmd.sdk.disable_subscribable.assert_called_once_with(dataset_id, version)
    assert output_with_argument(add_row, subscribable_item)
    mock_print.assert_called_once()


def test_add_sink(mock_event_stream_sdk, mocker, mock_print):
    set_argv(
        "events",
        "add-sink",
        f"ds:{dataset_id}/{version}",
        "--sink-type",
        sink_item["type"],
    )
    add_row = mocker.spy(TableOutput, "add_row")
    cmd = EventsCommand()
    mocker.spy(cmd.sdk, "add_sink")
    cmd.handler()
    cmd.sdk.add_sink.assert_called_once_with(
        dataset_id, version, sink_type=sink_item["type"]
    )
    assert output_with_argument(add_row, sink_item)
    mock_print.assert_called_once()


def test_remove_sink(mock_event_stream_sdk, mocker, mock_print):
    set_argv(
        "events", "remove-sink", f"ds:{dataset_id}/{version}", "--sink-id", sink_id
    )
    cmd = EventsCommand()
    mocker.spy(cmd.sdk, "remove_sink")
    cmd.handler()
    cmd.sdk.remove_sink.assert_called_once_with(dataset_id, version, sink_id=sink_id)
    mock_print.assert_called_once_with(sink_deleted_response["message"])


def test_put_event(mock_event_stream_sdk, mocker, mock_print):
    set_argv("events", "put", f"ds:{dataset_id}/{version}", "--file", "input.json")
    input_json = {"test": "event"}
    read_input = mocker.patch(
        f"{EventsCommand.__module__}.read_json", return_value=input_json
    )
    post_event = mocker.patch(
        f"{pipeline_client_qual}.post_event", return_value={"some": "response"}
    )
    cmd = EventsCommand()
    cmd.handler()

    assert read_input.called_once
    assert post_event.called_once_with(input_json, "dataset-id", "version-1")


def test_resolve_dataset_uri():
    cmd = EventsCommand()

    for dataset_uri in [
        dataset_id,
        f"{dataset_id}/{version}",
        f"{dataset_id}/{version}/",
        f"ds:{dataset_id}",
        f"ds:{dataset_id}/{version}",
        f"ds:{dataset_id}/{version}/",
        f"ds:{dataset_id}/{version}/abc",
    ]:
        cmd.args["<dataset-uri>"] = dataset_uri
        assert cmd._resolve_dataset_uri() == (dataset_id, version)


def test_resolve_dataset_uri_invalid():
    cmd = EventsCommand()

    for dataset_uri in [
        f"ds://{dataset_id}/{version}",
        f"ds://{dataset_id}/{version}",
        f"ab:{dataset_id}/{version}",
    ]:
        cmd.args["<dataset-uri>"] = dataset_uri
        with pytest.raises(SystemExit):
            cmd._resolve_dataset_uri()


@pytest.fixture()
def mock_event_stream_sdk(monkeypatch):
    def get_event_stream(self, dataset_id, version):
        return event_stream_item

    def create_event_stream(self, dataset_id, version, create_raw):
        return event_stream_item

    def delete_event_stream(self, dataset_id, version):
        return event_stream_item

    def get_subscribable(self, dataset_id, version):
        return subscribable_item

    def enable_subscribable(self, dataset_id, version):
        return subscribable_item

    def disable_subscribable(self, dataset_id, version):
        return subscribable_item

    def get_sinks(self, dataset_id, version):
        return [sink_item]

    def get_sink(self, dataset_id, version, sink_id):
        return [sink_item]

    def add_sink(self, dataset_id, version, sink_type):
        return sink_item

    def remove_sink(self, dataset_id, version, sink_id):
        return sink_deleted_response

    monkeypatch.setattr(EventStreamClient, "get_event_stream_info", get_event_stream)
    monkeypatch.setattr(EventStreamClient, "create_event_stream", create_event_stream)
    monkeypatch.setattr(EventStreamClient, "delete_event_stream", delete_event_stream)
    monkeypatch.setattr(EventStreamClient, "get_subscribable", get_subscribable)
    monkeypatch.setattr(EventStreamClient, "enable_subscribable", enable_subscribable)
    monkeypatch.setattr(EventStreamClient, "disable_subscribable", disable_subscribable)
    monkeypatch.setattr(EventStreamClient, "get_sink", get_sink)
    monkeypatch.setattr(EventStreamClient, "get_sinks", get_sinks)
    monkeypatch.setattr(EventStreamClient, "add_sink", add_sink)
    monkeypatch.setattr(EventStreamClient, "remove_sink", remove_sink)
