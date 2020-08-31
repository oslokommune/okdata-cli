from origocli.output import create_output
from origocli.commands.eventsng.base import BaseEventsCommand


class EventsCreateStream(BaseEventsCommand):
    """
    usage:
      origo eventsng create-stream <datasetid> <version> [--skip-raw] [options]

    options:
      -d --debug
      --format=<format>
    """

    def default(self):
        out = create_output(self.opt("format"), "events_stream_config.json")
        out.output_singular_object = True
        datasetid = self.arg("datasetid")
        version = self.arg("version")
        create_raw = not self.opt("skip-raw")
        self.log.info(
            f"Creating event stream for dataset {datasetid}/{version}, raw={create_raw}"
        )
        data = self.sdk.create_event_stream(datasetid, version, create_raw=create_raw)
        out.add_row(data)
        self.print(f"Creating event stream for {datasetid}/{version}", out)


class EventsLs(BaseEventsCommand):
    """
    usage:
      origo eventsng ls <datasetid> <version> [options]

    options:
      -d --debug
      --format=<format>
    """

    def default(self):
        out = create_output(self.opt("format"), "events_stream_config.json")
        out.output_singular_object = True
        datasetid = self.arg("datasetid")
        version = self.arg("version")
        self.log.info(f"Getting event stream for dataset {datasetid}/{version}")
        data = self.sdk.get_event_stream_info(datasetid, version)
        out.add_row(data)
        self.print(f"Event streams for {datasetid}/{version}", out)


class EventsDeleteStream(BaseEventsCommand):
    """
    usage:
      origo eventsng delete-stream <datasetid> <version> [options]

    options:
      -d --debug
      --format=<format>
    """

    def default(self):
        out = create_output(self.opt("format"), "events_stream_config.json")
        out.output_singular_object = True
        datasetid = self.arg("datasetid")
        version = self.arg("version")
        self.log.info(f"Deleting event stream for dataset {datasetid}/{version}")
        data = self.sdk.delete_event_stream(datasetid, version)
        out.add_row(data)
        self.print(f"Deleting event stream for {datasetid}/{version}", out)
