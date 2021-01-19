import pytest
from conftest import set_argv
from okdata.sdk.event.post_event import PostEvent
from okdata.sdk.event.event_stream_client import EventStreamClient
from okdata.cli.output import TableOutput
from okdata.cli.commands.events import EventsCommand


pipeline_client_qual = f"{PostEvent.__module__}.{PostEvent.__name__}"

dataset_id = "test-dataset"
version = "1"
sink_type = "s3"
event_stream_item = {
    "status": "ACTIVE",
    "updated_by": "knut",
    "updated_at": "2020-08-26T08:07:21.903672+00:00",
    "id": f"{dataset_id}/{version}",
    "create_raw": True,
    "deleted": False,
    "accessRights": "restricted",
}
subscribable_item = {
    "status": "INACTIVE",
    "updated_by": "janedone",
    "updated_at": "2020-08-20T06:51:42.786699+00:00",
    "enabled": False,
}
sink_item = {
    "type": sink_type,
    "status": "ACTIVE",
    "updated_by": "janedone",
    "updated_at": "2020-08-20T06:51:42.786699+00:00",
}
sink_deleted_response = {
    "message": f"Disabled sink of type {sink_type} for stream {dataset_id}/{version}"
}


def output_with_argument(output, argument):
    for (args, kwargs) in output.call_args_list:
        if argument in args:
            return True
    return False


def test_describe_stream(mock_event_stream_sdk, mocker, mock_print):
    set_argv("events", "describe-stream", f"ds:{dataset_id}/{version}")
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


def test_enable_subscription(mock_event_stream_sdk, mocker, mock_print):
    set_argv("events", "enable-subscription", f"ds:{dataset_id}/{version}")
    add_row = mocker.spy(TableOutput, "add_row")
    cmd = EventsCommand()
    mocker.spy(cmd.sdk, "enable_subscription")
    cmd.handler()
    cmd.sdk.enable_subscription.assert_called_once_with(dataset_id, version)
    assert output_with_argument(add_row, subscribable_item)
    mock_print.assert_called_once()


def test_disable_subscription(mock_event_stream_sdk, mocker, mock_print):
    set_argv("events", "disable-subscription", f"ds:{dataset_id}/{version}")
    add_row = mocker.spy(TableOutput, "add_row")
    cmd = EventsCommand()
    mocker.spy(cmd.sdk, "disable_subscription")
    cmd.handler()
    cmd.sdk.disable_subscription.assert_called_once_with(dataset_id, version)
    assert output_with_argument(add_row, subscribable_item)
    mock_print.assert_called_once()


def test_enable_sink(mock_event_stream_sdk, mocker, mock_print):
    set_argv(
        "events",
        "enable-sink",
        f"ds:{dataset_id}/{version}",
        "--sink-type",
        sink_item["type"],
    )
    add_row = mocker.spy(TableOutput, "add_row")
    cmd = EventsCommand()
    mocker.spy(cmd.sdk, "enable_sink")
    cmd.handler()
    cmd.sdk.enable_sink.assert_called_once_with(
        dataset_id, version, sink_type=sink_item["type"]
    )
    assert output_with_argument(add_row, sink_item)
    mock_print.assert_called_once()


def test_disable_sink(mock_event_stream_sdk, mocker, mock_print):
    set_argv(
        "events", "disable-sink", f"ds:{dataset_id}/{version}", "--sink-type", sink_type
    )
    cmd = EventsCommand()
    mocker.spy(cmd.sdk, "disable_sink")
    cmd.handler()
    cmd.sdk.disable_sink.assert_called_once_with(
        dataset_id, version, sink_type=sink_type
    )
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
        f"ds:{dataset_id}",
        f"ds:{dataset_id}/{version}",
        "ds:arsrapport/2",
        "ds:dette-er-1-test",
        "ds:dette-er-1-test/10",
        "ds:dataset-0-100-x-test/1",
        "ds:mange-versjoner/192",
    ]:
        cmd.args["<dataset-uri>"] = dataset_uri
        expected_dataset_id, _, expected_version = dataset_uri[3:].partition("/")
        expected_version = expected_version if expected_version else "1"
        assert cmd._resolve_dataset_uri() == (expected_dataset_id, expected_version)


def test_resolve_dataset_uri_unprefixed():
    cmd = EventsCommand()

    for dataset_uri in [
        dataset_id,
        f"{dataset_id}/{version}",
        "arsrapport/2",
        "dette-er-1-test",
        "dette-er-1-test/10",
        "dataset-0-100-x-test/1",
        "mange-versjoner/192",
    ]:
        cmd.args["<dataset-uri>"] = dataset_uri
        expected_dataset_id, _, expected_version = dataset_uri.partition("/")
        expected_version = expected_version if expected_version else "1"
        assert cmd._resolve_dataset_uri() == (expected_dataset_id, expected_version)


def test_resolve_dataset_uri_invalid():
    cmd = EventsCommand()

    for dataset_uri in [
        "årsrapport/1",
        f"{dataset_id}/",
        f"{dataset_id}/0",
        f"{dataset_id}/01",
        f"{dataset_id}/test",
        f"{dataset_id}/{version}/",
        f"{dataset_id}/{version}/20200101T111213",
        f"ds:{dataset_id}/",
        f"ds:{dataset_id}/{version}/",
        f"ds:{dataset_id}/{version}/20200101T111213",
        f"ds:{dataset_id}/{version}/20200101T111213/",
        f"ds://{dataset_id}/{version}",
        f"ds://{dataset_id}/{version}/",
        f"ab:{dataset_id}/{version}",
    ]:
        cmd.args["<dataset-uri>"] = dataset_uri
        with pytest.raises(ValueError):
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

    def enable_subscription(self, dataset_id, version):
        return subscribable_item

    def disable_subscription(self, dataset_id, version):
        return subscribable_item

    def get_sinks(self, dataset_id, version):
        return [sink_item]

    def get_sink(self, dataset_id, version, sink_type):
        return [sink_item]

    def enable_sink(self, dataset_id, version, sink_type):
        return sink_item

    def disable_sink(self, dataset_id, version, sink_type):
        return sink_deleted_response

    monkeypatch.setattr(EventStreamClient, "get_event_stream_info", get_event_stream)
    monkeypatch.setattr(EventStreamClient, "create_event_stream", create_event_stream)
    monkeypatch.setattr(EventStreamClient, "delete_event_stream", delete_event_stream)
    monkeypatch.setattr(EventStreamClient, "get_subscribable", get_subscribable)
    monkeypatch.setattr(EventStreamClient, "enable_subscription", enable_subscription)
    monkeypatch.setattr(EventStreamClient, "disable_subscription", disable_subscription)
    monkeypatch.setattr(EventStreamClient, "get_sink", get_sink)
    monkeypatch.setattr(EventStreamClient, "get_sinks", get_sinks)
    monkeypatch.setattr(EventStreamClient, "enable_sink", enable_sink)
    monkeypatch.setattr(EventStreamClient, "disable_sink", disable_sink)
