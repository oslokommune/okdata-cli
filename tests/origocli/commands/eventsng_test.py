from unittest.mock import ANY
from conftest import set_argv

from origocli.output import TableOutput
from origo.event.event_stream_client import EventStreamClient
from origocli.commands.eventsng.streams import (
    EventsCreateStream,
    EventsLs,
    EventsDeleteStream,
)

# from origocli.commands.eventsng.subscribable import (
#     EventsCheckSubscribable,
#     EventsEnableSubscribable,
#     EventsDisableSubscribable,
# )
# from origocli.commands.eventsng.sinks import (
#     EventsLsSinks,
#     EventsAddSink,
#     EventsRemoveSink,
# )


event_stream_client_qual = (
    f"{EventStreamClient.__module__}.{EventStreamClient.__name__}"
)
sdk = EventStreamClient()
dataset_id = "test-dataset"
version = "1"
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
            == '{"id": "test-dataset/1", "create_raw": true, "confidentiality": "yellow", "updated_by": "knut", "updated_at": "2020-08-26T08:07:21.903672+00:00", "deleted": false, "status": "ACTIVE"}'
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


"""
class TestEventsCheckSubscribable:
    def test_check_subscribable(self, mocker, mock_print):
        set_argv("eventsng", "check-subscribable", dataset_id, version)
        add_row = mocker.spy(TableOutput, "add_row")
        sdk_command = mocker.patch(
            f"{event_stream_client_qual}.get_subscribable",
            return_value=subscribable_item,
        )
        EventsCreateStream(sdk).handler()
        sdk_command.assert_called_once_with(
            dataset_id, version
        )
        add_row.assert_called_once_with(self=ANY, row=subscribable_item)
        mock_print.assert_called_once()
"""
