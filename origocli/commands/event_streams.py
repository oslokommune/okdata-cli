import json
from requests.exceptions import HTTPError

from origocli.command import BaseCommand

from origo.event.event_stream_client import EventStreamClient


class EventStreamCommand(BaseCommand):
    """Oslo :: Event streams

    Usage:
      origo event_streams create <datasetid> <version>
      origo event_streams ls <datasetid> <version>
      origo event_streams delete <datasetid> <version>

    Create an event stream:
        origo event_streams create some-dataset-id 1
        origo event_streams ls some-dataset-id 1
        origo event_streams delete some-dataset-id 1

    Options:
      -d --debug
      -h --help
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
        dataset_id = self.arg("datasetid")
        version = self.arg("version")
        resp = self.sdk.create_event_stream(dataset_id, version)
        self.print(resp["message"])

    def ls(self):
        dataset_id = self.arg("datasetid")
        version = self.arg("version")
        response = self.sdk.get_event_stream_info(dataset_id, version)
        self.print(json.dumps(response, indent=2))

    def delete(self):
        dataset_id = self.arg("datasetid")
        version = self.arg("version")
        self.sdk.delete_event_stream(dataset_id, version)
        self.print(f"Delete initiated")
