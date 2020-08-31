from origocli.output import create_output
from origocli.commands.eventsng.base import BaseEventsCommand


class EventsLsSinks(BaseEventsCommand):
    """
    usage:
      origo eventsng sinks <datasetid> <version> [--sink-id=<sink_id>] [options]

    options:
      -d --debug
      --format=<format>
    """

    def default(self):
        datasetid = self.arg("datasetid")
        version = self.arg("version")
        sink_id = self.opt("sink-id")
        out = create_output(self.opt("format"), "events_sink_config.json")

        if sink_id:
            out.output_singular_object = True
            data = self.sdk.get_sink(datasetid, version, sink_id)
            out.add_row(data)
            self.print(f"Sink for {datasetid}/{version}", out)
            return

        data = self.sdk.get_sinks(datasetid, version)
        out.add_rows(data)
        self.print(f"Sinks for {datasetid}/{version}", out)


class EventsAddSink(BaseEventsCommand):
    """
    usage:
      origo eventsng add-sink <datasetid> <version> --sink-type=<sink_type> [options]

    options:
      -d --debug
      --format=<format>
    """

    def default(self):
        datasetid = self.arg("datasetid")
        version = self.arg("version")
        sink_type = self.opt("sink-type")

        out = create_output(self.opt("format"), "events_sink_config.json")
        out.output_singular_object = True
        data = self.sdk.add_sink(datasetid, version, sink_type=sink_type)
        out.add_row(data)
        self.print(f"Adding sink for {datasetid}/{version}", out)


class EventsRemoveSink(BaseEventsCommand):
    """
    usage:
      origo eventsng remove-sink <datasetid> <version> --sink-id=<sink_id> [options]

    options:
      -d --debug
      --format=<format>
    """

    def default(self):
        datasetid = self.arg("datasetid")
        version = self.arg("version")
        sink_id = self.opt("sink-id")

        out = create_output(self.opt("format"), "events_sink_config.json")
        out.output_singular_object = True
        data = self.sdk.remove_sink(datasetid, version, sink_id=sink_id)
        self.print(data["message"])
