import json

from origo.config import Config
from origo.auth.auth import Authenticate
from origo.event.post_event import PostEvent
from origo.elasticsearch.queries import ElasticsearchQueries, NotDatasetOwnerError

from origocli.command import BaseCommand
from origocli.io import read_stdin_or_filepath


class PutEventsCommand(BaseCommand):
    """Oslo :: Put events

Usage:
  origo events put <datasetid> <versionid> [--file=<file>]

Send a event to your event stream:
  echo '{"hello": "world"}' | origo events put test-event 1
  echo '[{"hello": "world"}, {"world": "hello"}]' | origo events put test-event 1
  cat /tmp/event.json | origo events put test-event 1
  origo events put test-event 1 --file=/tmp/event.json

Options:
  --file=<file>
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        env = self.opt("env")

        config = Config(env=env)
        auth = Authenticate(config)
        auth.login()

        self.sdk = PostEvent(auth=auth, env=env)

    def handler(self):
        payload = read_stdin_or_filepath(self.opt("file"))
        self.log.info(f"Putting event with payload: {payload}")
        try:
            datasetid = self.arg("datasetid")
            versionid = self.arg("versionid")
            self.sdk.post_event(payload, datasetid, versionid)
            self.print("Done putting event")
        except Exception as e:
            self.log.info(f"Failed: {e}")
            self.print(f"Could not put event: {repr(e)}")


class EventsStatCommand(BaseCommand):
    """Oslo :: Event stat

Usage:
  origo events stat <datasetid>
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        env = self.opt("env")

        config = Config(env=env)
        auth = Authenticate(config)
        auth.login()

        self.sdk = ElasticsearchQueries(auth=auth, env=env)

    def handler(self):
        dataset_id = self.arg("datasetid")
        data = None

        try:
            data = self.sdk.event_stat(dataset_id)
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


class EventsRegistry(BaseCommand):
    """Oslo :: Events

Usage:
  origo events <command> [<args>...]
"""
    sub_commands = {
        "put": PutEventsCommand,
        "stat": EventsStatCommand,
    }
