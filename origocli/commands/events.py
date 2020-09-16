import re

from origo.event.post_event import PostEvent
from origo.elasticsearch.queries import ElasticsearchQueries
from origo.event.event_stream_client import EventStreamClient

from origocli.command import BaseCommand, BASE_COMMAND_OPTIONS
from origocli.io import read_json
from origocli.output import create_output


class EventsCommand(BaseCommand):
    __doc__ = f"""Oslo :: Events

Usage:
  origo events ls <dataset-uri> [options]
  origo events create-stream <dataset-uri> [--skip-raw] [options]
  origo events delete-stream <dataset-uri> [options]
  origo events enable-subscribable <dataset-uri> [options]
  origo events disable-subscribable <dataset-uri> [options]
  origo events add-sink <dataset-uri> --sink-type=<sink_type> [options]
  origo events remove-sink <dataset-uri> --sink-id=<sink_id> [options]
  origo events put <dataset-uri> [--file=<file> options]
  origo events stat <dataset-uri> [options]

Examples:
  origo events ls ds:my-dataset-id/1
  origo events ls my-dataset-id/1
  origo events ls my-dataset-id
  origo events create-stream ds:my-dataset-id/1
  origo events add-sink ds:my-dataset-id/1 --sink-type=s3
  origo events remove-sink ds:my-dataset-id/1 --sink-id=ab12c
  echo '{{"hello": "world"}}' | origo events put ds:my-dataset-id/1
  echo '[{{"hello": "world"}}, {{"world": "hello"}}]' | origo events put ds:my-dataset-id/1
  cat /tmp/event.json | origo events put ds:my-dataset-id/1
  origo events put ds:my-dataset-id/1 --file=/tmp/event.json
  origo events stat ds:my-dataset-id
  origo events stat ds:my-dataset-id --format=json | jq ".last_hour.events"

Options:{BASE_COMMAND_OPTIONS}
    """

    def __init__(self):
        super().__init__()
        env = self.opt("env")

        self.sdk = EventStreamClient(env=env)
        self.post_event_sdk = PostEvent(env=env)
        self.esq_sdk = ElasticsearchQueries(env=env)

        self.handler = self.default

    def default(self):
        self.log.info("EventsCommand.handle()")

        if self.cmd("ls"):
            self.stream()
        elif self.cmd("create-stream"):
            self.create_stream()
        elif self.cmd("delete-stream"):
            self.delete_stream()
        elif self.cmd("enable-subscribable"):
            self.enable_subscribable()
        elif self.cmd("disable-subscribable"):
            self.disable_subscribable()
        elif self.cmd("add-sink"):
            self.add_sink()
        elif self.cmd("remove-sink"):
            self.remove_sink()
        elif self.cmd("put"):
            self.put_event()
        elif self.cmd("stat"):
            self.event_stat()
        else:
            self.help()

    def streams(self):
        # TODO: List all events streams for given dataset
        pass

    def stream(self):
        dataset_id, version = self._resolve_dataset_uri()

        event_stream = self.sdk.get_event_stream_info(dataset_id, version)
        subscribable = self.sdk.get_subscribable(dataset_id, version)
        sinks = self.sdk.get_sinks(dataset_id, version)

        if self.opt("format") == "json":
            out = {}
            out["stream"] = event_stream
            out["subscribable"] = subscribable
            out["sinks"] = sinks
            self.print("", out)
            return

        out = create_output(self.opt("format"), "events_stream_config.json")
        out.output_singular_object = True
        out.add_row(event_stream)
        self.print(f"Event stream: {dataset_id}/{version}", out)

        out = create_output(self.opt("format"), "events_subscribable_config.json")
        out.output_singular_object = True
        out.add_row(subscribable)
        self.print("\n\nSubscribable for event stream:", out)

        out = create_output(self.opt("format"), "events_sink_config.json")
        out.add_rows(sinks)
        self.print("\n\nSinks for event stream:", out)

    def create_stream(self):
        dataset_id, version = self._resolve_dataset_uri()
        create_raw = not self.opt("skip-raw")
        event_stream = self.sdk.create_event_stream(
            dataset_id, version, create_raw=create_raw
        )
        out = create_output(self.opt("format"), "events_stream_config.json")
        out.output_singular_object = True
        out.add_row(event_stream)
        self.print(f"Creating event stream for {dataset_id}/{version}", out)

    def delete_stream(self):
        dataset_id, version = self._resolve_dataset_uri()
        event_stream = self.sdk.delete_event_stream(dataset_id, version)
        out = create_output(self.opt("format"), "events_stream_config.json")
        out.output_singular_object = True
        out.add_row(event_stream)
        self.print(f"Deleting event stream for {dataset_id}/{version}", out)

    def enable_subscribable(self):
        dataset_id, version = self._resolve_dataset_uri()
        subscribable = self.sdk.enable_subscribable(dataset_id, version)
        out = create_output(self.opt("format"), "events_subscribable_config.json")
        out.output_singular_object = True
        out.add_row(subscribable)
        self.print(
            f"Enabling subscribable event stream for {dataset_id}/{version}", out
        )

    def disable_subscribable(self):
        dataset_id, version = self._resolve_dataset_uri()
        subscribable = self.sdk.disable_subscribable(dataset_id, version)
        out = create_output(self.opt("format"), "events_subscribable_config.json")
        out.output_singular_object = True
        out.add_row(subscribable)
        self.print(
            f"Disabling subscribable event stream for {dataset_id}/{version}", out
        )

    def add_sink(self):
        dataset_id, version = self._resolve_dataset_uri()
        sink_type = self.opt("sink-type")
        sink = self.sdk.add_sink(dataset_id, version, sink_type=sink_type)
        out = create_output(self.opt("format"), "events_sink_config.json")
        out.output_singular_object = True
        out.add_row(sink)
        self.print(f"Adding sink for {dataset_id}/{version}", out)

    def remove_sink(self):
        dataset_id, version = self._resolve_dataset_uri()
        sink_id = self.opt("sink-id")
        response = self.sdk.remove_sink(dataset_id, version, sink_id=sink_id)
        if self.opt("format") == "json":
            self.print("", response)
            return
        self.print(response["message"])

    def put_event(self):
        dataset_id, version = self._resolve_dataset_uri()
        out = create_output(self.opt("format"), "events_put_event_config.json")
        out.output_singular_object = True
        payload = read_json(self.opt("file"))
        self.log.info(f"Putting event with payload: {payload}")

        self.post_event_sdk.post_event(payload, dataset_id, version)
        data = {
            "stream": dataset_id,
            "version": version,
            "source": self.opt("file") or "stdin",
            "status": "Commited",
        }
        out.add_row(data)
        self.print("Put event status", out)

    def event_stat(self):
        dataset_id, version = self._resolve_dataset_uri()
        out = create_output(self.opt("format"), "events_stat_config.json")

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

    def _resolve_dataset_uri(self):
        dataset_uri = self.arg("dataset-uri").lower()
        uri_pattern = r"^(?:ds:)?([a-z0-9\-]+)(?:\/|$)(?:([0-9]+))?"
        match = re.match(uri_pattern, dataset_uri)

        if not match:
            self.log.error(
                'Error: Invalid dataset URI, expects pattern "[ds:]<dataset_id>[/<version>]"'
            )
            raise SystemExit

        [dataset_id, version] = match.groups()

        version = version if version else "1"

        return dataset_id, version
