from origocli.output import create_output
from origocli.commands.eventsng.base import BaseEventsCommand


class EventsCheckSubscribable(BaseEventsCommand):
    """
    usage:
      origo eventsng check-subscribable <datasetid> <version> [options]

    options:
      -d --debug
      --format=<format>
    """

    def default(self):
        out = create_output(self.opt("format"), "events_subscribable_config.json")
        out.output_singular_object = True
        datasetid = self.arg("datasetid")
        version = self.arg("version")
        data = self.sdk.get_subscribable(datasetid, version)
        out.add_row(data)
        self.print(f"Subscribable event stream for {datasetid}/{version}", out)


class EventsEnableSubscribable(BaseEventsCommand):
    """
    usage:
      origo eventsng enable-subscribable <datasetid> <version> [options]

    options:
      -d --debug
      --format=<format>
    """

    def default(self):
        out = create_output(self.opt("format"), "events_subscribable_config.json")
        out.output_singular_object = True
        datasetid = self.arg("datasetid")
        version = self.arg("version")
        data = self.sdk.enable_subscribable(datasetid, version)
        out.add_row(data)
        self.print(f"Enabling subscribable event stream for {datasetid}/{version}", out)


class EventsDisableSubscribable(BaseEventsCommand):
    """
    usage:
      origo eventsng disable-subscribable <datasetid> <version> [options]

    options:
      -d --debug
      --format=<format>
    """

    def default(self):
        out = create_output(self.opt("format"), "events_subscribable_config.json")
        out.output_singular_object = True
        datasetid = self.arg("datasetid")
        version = self.arg("version")
        data = self.sdk.disable_subscribable(datasetid, version)
        out.add_row(data)
        self.print(
            f"Disabling subscribable event stream for {datasetid}/{version}", out
        )
