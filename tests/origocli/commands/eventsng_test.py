from unittest.mock import ANY
from conftest import set_argv

from origocli.output import TableOutput
from origo.event.event_stream_client import EventStreamClient
from origocli.commands.eventsng.streams import (
    EventsCreateStream,
    EventsLs,
    EventsDeleteStream,
)

from origocli.commands.eventsng.subscribable import (
    EventsCheckSubscribable,
    EventsEnableSubscribable,
    EventsDisableSubscribable,
)

from origocli.commands.eventsng.sinks import (
    EventsLsSinks,
    EventsAddSink,
    EventsRemoveSink,
)


event_stream_client_qual = (
    f"{EventStreamClient.__module__}.{EventStreamClient.__name__}"
)
sdk = EventStreamClient()
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


class TestEventsCreateStream:
    def test_create_stream(self, mocker, mock_print):
        set_argv("eventsng", "create-stream", dataset_id, version, "--skip-raw")
        add_row = mocker.spy(TableOutput, "add_row")
        create_event_stream = mocker.patch(
            f"{event_stream_client_qual}.create_event_stream",
            return_value=event_stream_item,
        )
        EventsCreateStream(sdk).handler()
        create_event_stream.assert_called_once_with(
            dataset_id, version, create_raw=False
        )
        add_row.assert_called_once_with(self=ANY, row=event_stream_item)
        mock_print.assert_called_once()

    def test_create_stream_as_json(self, mocker, capsys):
        set_argv("eventsng", "create-stream", dataset_id, version, "--format", "json")
        create_event_stream = mocker.patch(
            f"{event_stream_client_qual}.create_event_stream",
            return_value=event_stream_item,
        )
        EventsCreateStream(sdk).handler()
        create_event_stream.assert_called_once_with(
            dataset_id, version, create_raw=True
        )
        assert (
            capsys.readouterr().out.strip()
            == '{"id": "test-dataset/1", "create_raw": true, "confidentiality": "yellow", "deleted": false, "status": "ACTIVE", "updated_by": "knut", "updated_at": "2020-08-26T08:07:21.903672+00:00"}'
        )


class TestEventsLs:
    def test_event_streams(self, mocker, mock_print):
        set_argv("eventsng", "ls", dataset_id, version)
        add_row = mocker.spy(TableOutput, "add_row")
        get_event_stream = mocker.patch(
            f"{event_stream_client_qual}.get_event_stream_info",
            return_value=event_stream_item,
        )
        EventsLs(sdk).handler()
        get_event_stream.assert_called_once_with(dataset_id, version)
        add_row.assert_called_once_with(self=ANY, row=event_stream_item)
        mock_print.assert_called_once()


class TestEventsDeleteStream:
    def test_delete_stream(self, mocker, mock_print):
        set_argv("eventsng", "delete-stream", dataset_id, version)
        add_row = mocker.spy(TableOutput, "add_row")
        delete_event_stream = mocker.patch(
            f"{event_stream_client_qual}.delete_event_stream",
            return_value=event_stream_item,
        )
        EventsDeleteStream(sdk).handler()
        delete_event_stream.assert_called_once_with(dataset_id, version)
        add_row.assert_called_once_with(self=ANY, row=event_stream_item)
        mock_print.assert_called_once()


class TestEventsCheckSubscribable:
    def test_check_subscribable(self, mocker, mock_print):
        set_argv("eventsng", "check-subscribable", dataset_id, version)
        add_row = mocker.spy(TableOutput, "add_row")
        sdk_command = mocker.patch(
            f"{event_stream_client_qual}.get_subscribable",
            return_value=subscribable_item,
        )
        EventsCheckSubscribable(sdk).handler()
        sdk_command.assert_called_once_with(dataset_id, version)
        add_row.assert_called_once_with(self=ANY, row=subscribable_item)
        mock_print.assert_called_once()


class TestEventsEnableSubscribable:
    def test_enable_subscribable(self, mocker, mock_print):
        set_argv("eventsng", "enable-subscribable", dataset_id, version)
        add_row = mocker.spy(TableOutput, "add_row")
        sdk_command = mocker.patch(
            f"{event_stream_client_qual}.enable_subscribable",
            return_value=subscribable_item,
        )
        EventsEnableSubscribable(sdk).handler()
        sdk_command.assert_called_once_with(dataset_id, version)
        add_row.assert_called_once_with(self=ANY, row=subscribable_item)
        mock_print.assert_called_once()


class TestEventsDisableSubscribable:
    def test_disable_subscribable(self, mocker, mock_print):
        set_argv("eventsng", "disable-subscribable", dataset_id, version)
        add_row = mocker.spy(TableOutput, "add_row")
        sdk_command = mocker.patch(
            f"{event_stream_client_qual}.disable_subscribable",
            return_value=subscribable_item,
        )
        EventsDisableSubscribable(sdk).handler()
        sdk_command.assert_called_once_with(dataset_id, version)
        add_row.assert_called_once_with(self=ANY, row=subscribable_item)
        mock_print.assert_called_once()


class TestEventsLsSinks:
    def test_ls_sinks(self, mocker, mock_print):
        set_argv("eventsng", "sinks", dataset_id, version)
        add_rows = mocker.spy(TableOutput, "add_rows")
        sdk_command = mocker.patch(
            f"{event_stream_client_qual}.get_sinks",
            return_value=[sink_item],
        )
        EventsLsSinks(sdk).handler()
        sdk_command.assert_called_once_with(dataset_id, version)
        add_rows.assert_called_once_with(self=ANY, rows=[sink_item])
        mock_print.assert_called_once()

    def test_ls_sinks_with_id(self, mocker, mock_print):
        set_argv("eventsng", "sinks", dataset_id, version, "--sink-id", sink_id)
        add_row = mocker.spy(TableOutput, "add_row")
        sdk_command = mocker.patch(
            f"{event_stream_client_qual}.get_sink",
            return_value=sink_item,
        )
        EventsLsSinks(sdk).handler()
        sdk_command.assert_called_once_with(dataset_id, version, sink_id=sink_id)
        add_row.assert_called_once_with(self=ANY, row=sink_item)
        mock_print.assert_called_once()


class TestEventsAddSink:
    def test_add_sink(self, mocker, mock_print):
        set_argv(
            "eventsng",
            "add-sink",
            dataset_id,
            version,
            "--sink-type",
            sink_item["type"],
        )
        add_row = mocker.spy(TableOutput, "add_row")
        sdk_command = mocker.patch(
            f"{event_stream_client_qual}.add_sink",
            return_value=sink_item,
        )
        EventsAddSink(sdk).handler()
        sdk_command.assert_called_once_with(
            dataset_id, version, sink_type=sink_item["type"]
        )
        add_row.assert_called_once_with(self=ANY, row=sink_item)
        mock_print.assert_called_once()


class TestEventsRemoveSink:
    def test_remove_sink(self, mocker, mock_print):
        set_argv(
            "eventsng",
            "remove-sink",
            dataset_id,
            version,
            "--sink-id",
            sink_id,
        )
        sdk_command = mocker.patch(
            f"{event_stream_client_qual}.remove_sink",
            return_value=sink_deleted_response,
        )
        EventsRemoveSink(sdk).handler()
        sdk_command.assert_called_once_with(dataset_id, version, sink_id=sink_id)
        mock_print.assert_called_once()
