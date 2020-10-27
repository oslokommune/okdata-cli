from origocli.command import BaseCommand, BASE_COMMAND_OPTIONS
from origocli.output import create_output

from origo.status import Status


class StatusCommand(BaseCommand):
    __doc__ = f"""Oslo :: Status

Usage:
  origo status <trace_id> [options --history]

Examples:
  origo status trace-id-from-system
  origo status trace-id-from-system --format=json | jq ".done"
  origo status trace-id-from-system --history

Options:{BASE_COMMAND_OPTIONS}
  --history
    """

    def __init__(self):
        super().__init__()
        env = self.opt("env")
        self.sdk = Status(env=env)
        self.handler = self.default

    def login(self):
        self.sdk.login()

    def default(self):
        self.log.info("StatusCommand.default()")
        if self.arg("trace_id"):
            self.status_for_id()
        else:
            self.print("Invalid command")

    @staticmethod
    def add_status_for_id_rows(out, trace_id, trace_events):
        finished = False
        trace_status = trace_events[-1]["trace_status"]
        trace_event_status = trace_events[-1]["trace_event_status"]

        for i, trace_event in enumerate(trace_events, 1):
            if trace_event["trace_status"] == "FINISHED":
                trace_event["done"] = False
                if trace_event["trace_event_status"] == "OK":
                    trace_event["done"] = True
                    finished = True
                    out.add_row(trace_event)

        if not finished:
            out.add_row(
                {
                    "done": False,
                    "trace_id": trace_id,
                    "trace_status": trace_status,
                    "trace_event_status": trace_event_status,
                }
            )

    def full_history_for_status(self, trace_id, trace_events):
        if trace_events:
            out = create_output(self.opt("format"), "status_history_config.json")
            out.add_rows(trace_events)
            self.print(f"Status for: {trace_id}", out)
        else:
            self.print(
                "No history found for status",
                {"error": 1, "message": "No trace events found"},
            )

    def status_for_id(self):
        trace_id = self.arg("trace_id")
        self.log.info(f"Looking up status: {trace_id}")
        trace_events = self.sdk.get_status(trace_id)
        if self.opt("history"):
            self.full_history_for_status(trace_id, trace_events)
        else:
            out = create_output(self.opt("format"), "status_config.json")
            out.output_singular_object = True
            StatusCommand.add_status_for_id_rows(out, trace_id, trace_events)
            self.print(f"Status for: {trace_id}", out)
