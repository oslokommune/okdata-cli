import pytest
from unittest.mock import ANY
from conftest import set_argv
from okdata.cli.commands.status import StatusCommand
from okdata.sdk.status import Status
from okdata.cli.output import TableOutput


successful_trace_id = "my-dataset-be0a4c02-9733-4ff8-af1b-cd14985e9e06"
successful_trace = [
    {
        "trace_event_status": "OK",
        "component": "data-uploader",
        "status_body": "N/A",
        "trace_status": "STARTED",
        "s3_path": "raw/green/my-dataset/version=1/edition=20200101T114457/test.json",
        "user": "data-uploader",
        "domain_id": "my-dataset",
        "start_time": "2020-01-01T12:44:59.454381",
        "trace_event_id": "19e3500f-7778-471f-8dc2-3bbcf9a95050",
        "end_time": "N/A",
        "trace_id": successful_trace_id,
        "domain": "dataset",
    },
    {
        "trace_event_status": "OK",
        "component": "copy",
        "status_body": {},
        "trace_status": "CONTINUE",
        "meta": {},
        "user": "na",
        "domain_id": "na",
        "start_time": "2020-01-01T12:45:04.653306",
        "trace_event_id": "f27b4377-1440-4e9b-9a9d-074330b0d0cf",
        "end_time": "2020-01-01T12:45:07.380869",
        "trace_id": successful_trace_id,
        "domain": "s3-writer",
    },
    {
        "trace_event_status": "OK",
        "component": "pipeline-instance",
        "trace_status": "FINISHED",
        "user": "system",
        "domain_id": "na",
        "start_time": "2020-01-01T12:45:08.332264",
        "trace_event_id": "fca42ffd-ea61-412c-9caa-671543c476a3",
        "end_time": "2020-01-01T12:45:08.332283",
        "trace_id": successful_trace_id,
        "domain": "dataset",
    },
]
in_progress_trace_id = "my-dataset-be270876-bdc8-4390-a56a-4c339dcef4ce"
in_progress_trace = [
    {
        "trace_event_status": "OK",
        "component": "data-uploader",
        "status_body": "N/A",
        "trace_status": "STARTED",
        "s3_path": "raw/green/my-dataset/version=1/edition=20200101T114457/test.json",
        "user": "data-uploader",
        "domain_id": "my-dataset",
        "start_time": "2020-01-01T12:44:59.454381",
        "trace_event_id": "2c9c0128-185c-4af7-9d76-e5779e525f37",
        "end_time": "N/A",
        "trace_id": in_progress_trace_id,
        "domain": "dataset",
    },
    {
        "trace_event_status": "OK",
        "component": "copy",
        "status_body": {},
        "trace_status": "CONTINUE",
        "meta": {},
        "user": "na",
        "domain_id": "na",
        "start_time": "2020-01-01T12:45:04.653306",
        "trace_event_id": "e1d4a84c-9f3c-48a9-95da-4d18cffb1f4a",
        "end_time": "2020-01-01T12:45:07.380869",
        "trace_id": in_progress_trace_id,
        "domain": "s3-writer",
    },
]
failed_trace_id = "my-dataset-0e1a102f-624d-41d3-8ff3-a78c050e97a6"
failed_trace = [
    {
        "trace_event_status": "OK",
        "component": "data-uploader",
        "status_body": "N/A",
        "trace_status": "STARTED",
        "s3_path": "raw/green/my-dataset/version=1/edition=20200101T112403/foo.csv",
        "user": "data-uploader",
        "domain_id": "my-dataset",
        "start_time": "2020-01-01T11:45:03.300316",
        "trace_event_id": "8b6b353f-d4fb-44dc-879b-911224663385",
        "end_time": "N/A",
        "trace_id": failed_trace_id,
        "domain": "dataset",
    },
    {
        "trace_event_status": "FAILED",
        "component": "pipeline-instance",
        "trace_status": "FINISHED",
        "user": "system",
        "domain_id": "na",
        "start_time": "2020-01-01T11:45:13.939324",
        "trace_event_id": "843c18ae-ab87-4c39-8dab-3ce5c4e2faf8",
        "end_time": "2020-01-01T11:45:13.939343",
        "trace_id": failed_trace_id,
        "domain": "dataset",
    },
]


def test_get_status(mock_status_sdk, mocker, mock_print):
    set_argv("status", successful_trace_id)
    cmd = StatusCommand()
    mocker.spy(cmd.sdk, "get_status")
    mocker.spy(cmd, "latest_event_for_status")
    mocker.spy(StatusCommand, "find_latest_event")
    mocker.spy(TableOutput, "add_row")
    cmd.handler()
    cmd.sdk.get_status.assert_called_once_with(successful_trace_id)
    cmd.latest_event_for_status.assert_called_once_with(
        successful_trace_id, successful_trace
    )
    StatusCommand.find_latest_event.assert_called_once_with(successful_trace)
    expected_event = successful_trace[-1]
    TableOutput.add_row.assert_called_once_with(
        ANY,
        {
            "done": True,
            "trace_id": expected_event["trace_id"],
            "trace_status": expected_event["trace_status"],
            "trace_event_status": expected_event["trace_event_status"],
        },
    )


def test_get_status_in_progress(mock_status_sdk, mocker, mock_print):
    set_argv("status", in_progress_trace_id)
    cmd = StatusCommand()
    mocker.spy(cmd.sdk, "get_status")
    mocker.spy(cmd, "latest_event_for_status")
    mocker.spy(StatusCommand, "find_latest_event")
    mocker.spy(TableOutput, "add_row")
    cmd.handler()
    cmd.sdk.get_status.assert_called_once_with(in_progress_trace_id)
    cmd.latest_event_for_status.assert_called_once_with(
        in_progress_trace_id, in_progress_trace
    )
    StatusCommand.find_latest_event.assert_called_once_with(in_progress_trace)
    expected_event = in_progress_trace[-1]
    TableOutput.add_row.assert_called_once_with(
        ANY,
        {
            "done": False,
            "trace_id": expected_event["trace_id"],
            "trace_status": expected_event["trace_status"],
            "trace_event_status": expected_event["trace_event_status"],
        },
    )


def test_get_status_failed(mock_status_sdk, mocker):
    set_argv("status", failed_trace_id)
    cmd = StatusCommand()
    mocker.spy(cmd.sdk, "get_status")
    mocker.spy(cmd, "latest_event_for_status")
    mocker.spy(StatusCommand, "find_latest_event")
    mocker.spy(TableOutput, "add_row")
    cmd.handler()
    cmd.sdk.get_status.assert_called_once_with(failed_trace_id)
    cmd.latest_event_for_status.assert_called_once_with(failed_trace_id, failed_trace)
    StatusCommand.find_latest_event.assert_called_once_with(failed_trace)
    expected_event = failed_trace[-1]
    TableOutput.add_row.assert_called_once_with(
        ANY,
        {
            "done": True,
            "trace_id": expected_event["trace_id"],
            "trace_status": expected_event["trace_status"],
            "trace_event_status": expected_event["trace_event_status"],
        },
    )


def test_get_status_with_history(mock_status_sdk, mocker):
    set_argv("status", successful_trace_id, "--history")
    cmd = StatusCommand()
    mocker.spy(cmd.sdk, "get_status")
    mocker.spy(cmd, "full_history_for_status")
    mocker.spy(TableOutput, "add_rows")
    cmd.handler()
    cmd.sdk.get_status.assert_called_once_with(successful_trace_id)
    cmd.full_history_for_status.assert_called_once()
    TableOutput.add_rows.assert_called_once_with(ANY, successful_trace)


@pytest.fixture()
def mock_status_sdk(monkeypatch):
    def get_status_return(self, uuid):
        if uuid == failed_trace_id:
            return failed_trace
        elif uuid == in_progress_trace_id:
            return in_progress_trace
        else:
            return successful_trace

    monkeypatch.setattr(Status, "get_status", get_status_return)
