from origo.event.event_stream_client import EventStreamClient

from origocli.command import BaseCommand
from origocli.commands.eventsng.streams import (
    EventsCreateStream,
    EventsLs,
    EventsDeleteStream,
)
from origocli.commands.eventsng.subscribable import (
    EventsCheckSubscribable,
    EventsEnableSubscribable,
    EventsDisableSubscribable,
)
from origocli.commands.eventsng.sinks import (
    EventsLsSinks,
    EventsAddSink,
    EventsRemoveSink,
)


class Events(BaseCommand):
    """
    usage:
      origo eventsng create-stream <datasetid> <version> [--skip-raw] [options]
      origo eventsng ls <datasetid> <version> [options]
      origo eventsng delete-stream <datasetid> <version> [options]
      origo eventsng check-subscribable <datasetid> <version> [options]
      origo eventsng enable-subscribable <datasetid> <version> [options]
      origo eventsng disable-subscribable <datasetid> <version> [options]
      origo eventsng sinks <datasetid> <version> [--sink-id=<sink_id>] [options]
      origo eventsng add-sink <datasetid> <version> --sink-type=<sink_type> [options]
      origo eventsng remove-sink <datasetid> <version> --sink-id=<sink_id> [options]

    options:
      -d --debug
      --format=<format>
    """

    def __init__(self):
        super().__init__()
        self.sdk = EventStreamClient()
        self.sdk.login()
        self.handler = self.default
        self.sub_commands = [
            EventsCreateStream,
            EventsLs,
            EventsDeleteStream,
            EventsCheckSubscribable,
            EventsEnableSubscribable,
            EventsDisableSubscribable,
            EventsLsSinks,
            EventsAddSink,
            EventsRemoveSink,
        ]

    def default(self):
        self.help()
