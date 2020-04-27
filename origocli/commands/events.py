from origo.config import Config
from origo.auth.auth import Authenticate
from origo.event.post_event import PostEvent
from origo.elasticsearch.queries import ElasticsearchQueries

from origocli.command import BaseCommand, BASE_COMMAND_OPTIONS
from origocli.io import read_stdin_or_filepath
from origocli.output import create_output


class EventsCommand(BaseCommand):
    __doc__ = f"""Oslo :: Events

Usage:
  origo events put <datasetid> <versionid> [--file=<file> options]
  origo events stat <datasetid> [options]

Examples:
  echo '{{"hello": "world"}}' | origo events put test-event 1
  echo '[{{"hello": "world"}}, {{"world": "hello"}}]' | origo events put test-event 1
  cat /tmp/event.json | origo events put test-event 1
  origo events put test-event 1 --file=/tmp/event.json
  origo events stat test-event
  origo events stat test-event --format=json | jq ".last_hour.events"

Options:{BASE_COMMAND_OPTIONS}
    """

    def __init__(self):
        super().__init__()
        env = self.opt("env")

        config = Config(env=env)
        self.auth = Authenticate(config)

        self.post_event_sdk = PostEvent(auth=self.auth, env=env)
        self.esq_sdk = ElasticsearchQueries(auth=self.auth, env=env)

        self.handler = self.default

    def login(self):
        self.auth.login()

    def default(self):
        self.log.info("EventsCommand.handle()")

        if self.cmd("put"):
            self.put_event()
        elif self.cmd("stat"):
            self.event_stat()
        else:
            self.print("Invalid command")

    def put_event(self):
        out = create_output(self.opt("format"), "event_stream_put_config.json")
        out.output_singular_object = True
        payload = read_stdin_or_filepath(self.opt("file"))
        self.log.info(f"Putting event with payload: {payload}")

        datasetid = self.arg("datasetid")
        versionid = self.arg("versionid")
        self.post_event_sdk.post_event(payload, datasetid, versionid)
        data = {
            "stream": datasetid,
            "version": versionid,
            "source": self.opt("file") or "stdin",
            "status": "Commited",
        }
        out.add_row(data)
        self.print("Put event status", out)

    def event_stat(self):
        out = create_output(self.opt("format"), "event_stream_stat_config.json")
        dataset_id = self.arg("datasetid")

        data = self.esq_sdk.event_stat(dataset_id)
        if self.opt("format") == "json":
            self.print("", data)
        else:
            hour = data["last_hour"]
            hour["timespan"] = "Last hour"
            day = data["last_day"]
            day["timespan"] = "Last day"
            week = data["last_week"]
            week["timespan"] = "Last week"
            outdata = [hour, day, week]
            out.add_rows(outdata)
            self.print(f"Events for {dataset_id}", out)
