from conftest import set_argv
from origocli.commands.events import EventsCommand
from origo.event.post_event import PostEvent


pipeline_client_qual = f"{PostEvent.__module__}.{PostEvent.__name__}"


def raiseEx(*args):
    raise Exception("test")


def test_handler(mocker):
    set_argv("events", "put", "dataset-id", "version-1", "--file", "input.json")
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
