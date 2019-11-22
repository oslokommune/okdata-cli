"""Oslo :: Datasets

Usage:
  origo events put <datasetid> <versionid> [--file=<file> options]

Send a event to your event stream:
    echo '{"hello": "world"}' | origo events put test-event 1
    echo '[{"hello": "world"}, {"world": "hello"}]' | origo events put test-event 1
    cat /tmp/event.json | origo events put test-event 1
    origo events put test-event 1 --file=/tmp/event.json

Options:
  -d --debug

"""

from origocli.command import Command
from origocli.io import read_stdin_or_filepath

from origo.event.post_event import PostEvent


class EventsCommand(Command):
    def __init__(self):
        super().__init__(__doc__)
        env = self.opt("env")
        self.event = PostEvent(env=env)
        self.event.login()

    def handle(self):
        self.log.info("EventsCommand.handle()")
        if self.cmd("put") is True:
            self.put_event()
        else:
            Command.help()

    def put_event(self):
        payload = read_stdin_or_filepath(self.opt("file"))
        self.log.info(f"Putting event with payload: {payload}")
        try:
            datasetid = self.arg("datasetid")
            versionid = self.arg("versionid")
            self.event.post_event(payload, datasetid, versionid)
            self.print("Done putting event")
        except Exception as e:
            self.log.info(f"Failed: {e}")
            self.print(f"Could not put event: {repr(e)}")
