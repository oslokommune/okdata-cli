import json

from origo.config import Config
from origo.auth.auth import Authenticate
from origo.event.post_event import PostEvent
from origo.elasticsearch.queries import ElasticsearchQueries, NotDatasetOwnerError

from origocli.command import BaseCommand
from origocli.io import read_stdin_or_filepath


class EventsCommand(BaseCommand):
    """Oslo :: Datasets

    Usage:
      origo events put <datasetid> <versionid> [--file=<file> options]
      origo events stat <datasetid> [options]

    Send a event to your event stream:
        echo '{"hello": "world"}' | origo events put test-event 1
        echo '[{"hello": "world"}, {"world": "hello"}]' | origo events put test-event 1
        cat /tmp/event.json | origo events put test-event 1
        origo events put test-event 1 --file=/tmp/event.json

    Options:
      -d --debug
      --format=<format>
    """

    def __init__(self):
        super().__init__()
        env = self.opt("env")

        config = Config(env=env)
        auth = Authenticate(config)
        auth.login()

        self.post_event_sdk = PostEvent(auth=auth, env=env)
        self.esq_sdk = ElasticsearchQueries(auth=auth, env=env)

        self.handler = self.default

    def default(self):
        self.log.info("EventsCommand.handle()")

        if self.cmd("put"):
            self.put_event()
        elif self.cmd("stat"):
            self.event_stat()
        else:
            self.print("Invalid command")

    def put_event(self):
        payload = read_stdin_or_filepath(self.opt("file"))
        self.log.info(f"Putting event with payload: {payload}")
        try:
            datasetid = self.arg("datasetid")
            versionid = self.arg("versionid")
            self.post_event_sdk.post_event(payload, datasetid, versionid)
            self.print("Done putting event")
        except Exception as e:
            self.log.info(f"Failed: {e}")
            self.print(f"Could not put event: {repr(e)}")

    def event_stat(self):
        dataset_id = self.arg("datasetid")
        data = None

        try:
            data = self.esq_sdk.event_stat(dataset_id)
        except NotDatasetOwnerError:
            self.print(f"You are not the owner of: {dataset_id}")
            return

        last_hour = data["last_hour"]["events"]
        last_day = data["last_day"]["events"]
        last_week = data["last_week"]["events"]

        payload = None
        if self.opt("format") == "json":
            payload = json.dumps(data)

        self.print("Events ...")
        self.print("Last hour\tLast day\tLast week")
        self.print(f"{last_hour}\t\t{last_day}\t\t{last_week}", payload)
