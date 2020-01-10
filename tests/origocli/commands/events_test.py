import logging

from conftest import set_argv, BASECMD_QUAL
from origocli.commands.events import EventsCommand
from origo.event.post_event import PostEvent


pipeline_client_qual = f"{PostEvent.__module__}.{PostEvent.__name__}"


def raiseEx(*args):
    raise Exception("test")


def test_handler(mocker):
    set_argv("events", "put", "dataset-id", "version-1", "--file", "input.json")
    input_json = {"test": "event"}
    read_input = mocker.patch(
        f"{EventsCommand.__module__}.read_stdin_or_filepath", return_value=input_json
    )
    post_event = mocker.patch(
        f"{pipeline_client_qual}.post_event", return_value={"some": "response"}
    )
    cmd = EventsCommand()
    cmd.handler()

    assert read_input.called_once
    assert post_event.called_once_with(input_json, "dataset-id", "version-1")


def test_handler_error(mocker, caplog):
    set_argv("events", "put", "dataset-id", "version-1", "--file", "input.json", "-d")
    input_json = {"test": "event"}
    caplog.set_level(logging.INFO)
    read_input = mocker.patch(
        f"{EventsCommand.__module__}.read_stdin_or_filepath", return_value=input_json
    )
    mocker.patch(f"{pipeline_client_qual}.post_event", new=raiseEx)
    print_err = mocker.patch(f"{BASECMD_QUAL}.print")
    cmd = EventsCommand()

    cmd.handler()

    assert read_input.called_once
    assert any(record.message.startswith("Failed: test") for record in caplog.records)
    assert print_err.called_once_with(f"Could not put event: test")
