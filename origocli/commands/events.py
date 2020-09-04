from origo.event.post_event import PostEvent
from origo.elasticsearch.queries import ElasticsearchQueries
from origo.event.event_stream_client import EventStreamClient

from origocli.command import BaseCommand, BASE_COMMAND_OPTIONS
from origocli.io import read_json
from origocli.output import create_output


class EventsCommand(BaseCommand):
    __doc__ = f"""Oslo :: Events

Usage:
  origo events ls <datasetid> <versionid> [options]
  origo events create-stream <datasetid> <versionid> [--skip-raw] [options]
  origo events delete-stream <datasetid> <versionid> [options]
  origo events enable-subscribable <datasetid> <versionid> [options]
  origo events disable-subscribable <datasetid> <versionid> [options]
  origo events add-sink <datasetid> <versionid> --sink-type=<sink_type> [options]
  origo events remove-sink <datasetid> <versionid> --sink-id=<sink_id> [options]
  origo events put <datasetid> <versionid> [--file=<file> options]
  origo events stat <datasetid> [options]

Examples:
  origo events ls my-dataset-id 1
  origo events create-stream my-dataset-id 1
  origo events add-sink my-dataset-id 1 --sink-type=s3
  origo events remove-sink my-dataset-id 1 --sink-id=ab12c
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

        self.sdk = EventStreamClient(env=env)
        self.post_event_sdk = PostEvent(env=env)
        self.esq_sdk = ElasticsearchQueries(env=env)

        self.handler = self.default

    def default(self):
        self.log.info("EventsCommand.handle()")

        if self.cmd("ls"):
            if self.arg("versionid"):
                self.stream()
            else:
                self.streams()
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
        dataset_id = self.arg("datasetid")
        version_id = self.arg("versionid")

        event_stream = self.sdk.get_event_stream_info(dataset_id, version_id)
        subscribable = self.sdk.get_subscribable(dataset_id, version_id)
        sinks = self.sdk.get_sinks(dataset_id, version_id)

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
        self.print(f"Event stream: {dataset_id}/{version_id}", out)

        out = create_output(self.opt("format"), "events_subscribable_config.json")
        out.output_singular_object = True
        out.add_row(subscribable)
        self.print("\n\nSubscribable for event stream:", out)

        out = create_output(self.opt("format"), "events_sink_config.json")
        out.add_rows(sinks)
        self.print("\n\nSinks for event stream:", out)

    def create_stream(self):
        dataset_id = self.arg("datasetid")
        version_id = self.arg("versionid")
        create_raw = not self.opt("skip-raw")
        event_stream = self.sdk.create_event_stream(
            dataset_id, version_id, create_raw=create_raw
        )
        out = create_output(self.opt("format"), "events_stream_config.json")
        out.output_singular_object = True
        out.add_row(event_stream)
        self.print(f"Creating event stream for {dataset_id}/{version_id}", out)

    def delete_stream(self):
        dataset_id = self.arg("datasetid")
        version_id = self.arg("versionid")
        event_stream = self.sdk.delete_event_stream(dataset_id, version_id)
        out = create_output(self.opt("format"), "events_stream_config.json")
        out.output_singular_object = True
        out.add_row(event_stream)
        self.print(f"Deleting event stream for {dataset_id}/{version_id}", out)

    def enable_subscribable(self):
        dataset_id = self.arg("datasetid")
        version_id = self.arg("versionid")
        subscribable = self.sdk.enable_subscribable(dataset_id, version_id)
        out = create_output(self.opt("format"), "events_subscribable_config.json")
        out.output_singular_object = True
        out.add_row(subscribable)
        self.print(
            f"Enabling subscribable event stream for {dataset_id}/{version_id}", out
        )

    def disable_subscribable(self):
        dataset_id = self.arg("datasetid")
        version_id = self.arg("versionid")
        subscribable = self.sdk.disable_subscribable(dataset_id, version_id)
        out = create_output(self.opt("format"), "events_subscribable_config.json")
        out.output_singular_object = True
        out.add_row(subscribable)
        self.print(
            f"Disabling subscribable event stream for {dataset_id}/{version_id}", out
        )

    def add_sink(self):
        dataset_id = self.arg("datasetid")
        version_id = self.arg("versionid")
        sink_type = self.opt("sink-type")
        sink = self.sdk.add_sink(dataset_id, version_id, sink_type=sink_type)
        out = create_output(self.opt("format"), "events_sink_config.json")
        out.output_singular_object = True
        out.add_row(sink)
        self.print(f"Adding sink for {dataset_id}/{version_id}", out)

    def remove_sink(self):
        dataset_id = self.arg("datasetid")
        version_id = self.arg("versionid")
        sink_id = self.opt("sink-id")
        response = self.sdk.remove_sink(dataset_id, version_id, sink_id=sink_id)
        if self.opt("format") == "json":
            self.print("", response)
            return
        self.print(response["message"])

    def put_event(self):
        datasetid = self.arg("datasetid")
        versionid = self.arg("versionid")

        out = create_output(self.opt("format"), "events_put_event_config.json")
        out.output_singular_object = True
        payload = read_json(self.opt("file"))
        self.log.info(f"Putting event with payload: {payload}")

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
        dataset_id = self.arg("datasetid")
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
