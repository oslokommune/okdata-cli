from origocli.command import BaseCommand, BASE_COMMAND_OPTIONS
from origocli.output import create_output

from origo.event.event_stream_client import EventStreamClient


class EventStreamCommand(BaseCommand):
    __doc__ = f"""Oslo :: Event streams

Usage:
  origo event_streams create <datasetid> <version> [options]
  origo event_streams ls <datasetid> <version> [options]
  origo event_streams delete <datasetid> <version> [options]

Examples:
  origo event_streams create some-dataset-id 1
  origo event_streams ls test-event-stream 1 --format=json | jq ".status" -r
  origo event_streams delete some-dataset-id 1

Options:{BASE_COMMAND_OPTIONS}
    """

    def __init__(self):
        super().__init__()
        env = self.opt("env")
        self.sdk = EventStreamClient(env=env)
        self.handler = self.default

    def default(self):
        if self.cmd("create"):
            self.create()
        elif self.cmd("ls"):
            self.ls()
        elif self.cmd("delete"):
            self.delete()
        else:
            self.print("Invalid command")

    def create(self):
        out = create_output(self.opt("format"), "event_streams_create_config.json")
        out.output_singular_object = True
        dataset_id = self.arg("datasetid")
        version = self.arg("version")
        resp = self.sdk.create_event_stream(dataset_id, version)
        data = {"id": f"{dataset_id}/{version}", "status": resp["message"]}
        out.add_row(data)
        self.print("Creating event stream", out)

    def ls(self):
        out = create_output(self.opt("format"), "event_streams_ls_config.json")
        out.output_singular_object = True
        dataset_id = self.arg("datasetid")
        version = self.arg("version")
        response = self.sdk.get_event_stream_info(dataset_id, version)
        out.add_row(response)
        self.print(f"Event Stream: {dataset_id}", out)

    def delete(self):
        out = create_output(self.opt("format"), "event_streams_delete_config.json")
        out.output_singular_object = True
        dataset_id = self.arg("datasetid")
        version = self.arg("version")
        self.sdk.delete_event_stream(dataset_id, version)
        data = {"id": f"{dataset_id}/{version}", "status": "Delete initiated"}
        out.add_row(data)
        self.print("Deleting event stream:", out)
