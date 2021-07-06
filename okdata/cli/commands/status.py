from okdata.cli.command import BaseCommand, BASE_COMMAND_OPTIONS
from okdata.cli.output import create_output

from okdata.sdk.status import Status


class StatusCommand(BaseCommand):
    __doc__ = f"""Oslo :: Status

Usage:
  okdata status <trace_id> [options --history]

Examples:
  okdata status trace-id-from-system
  okdata status trace-id-from-system --format=json | jq ".done"
  okdata status trace-id-from-system --history

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
    def find_latest_event(trace_events):
        for trace_event in trace_events:
            if trace_event["trace_status"] == "FINISHED":
                return trace_event
        return trace_events[-1]

    @staticmethod
    def get_error_messages(trace_events):
        for event in trace_events:
            error_messages = []
            for error in event.get("errors", []):
                try:
                    error_messages.append(error["message"]["en"])
                except (TypeError, KeyError):
                    pass
            event["errors"] = error_messages
        return trace_events

    def latest_event_for_status(self, trace_id, trace_events):
        # Collect errors from all events
        errors = []
        for event in trace_events:
            errors += event.get("errors", [])

        latest_event = StatusCommand.find_latest_event(trace_events)
        trace_status = latest_event["trace_status"]

        out = create_output(self.opt("format"), "status_config.json")
        out.output_singular_object = True
        out.add_row(
            {
                "done": trace_status == "FINISHED",
                "trace_id": trace_id,
                "trace_status": trace_status,
                "trace_event_status": latest_event["trace_event_status"],
                "errors": errors,
            }
        )
        self.print(f"Status for: {trace_id}", out)

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
        trace_events = StatusCommand.get_error_messages(trace_events)
        if self.opt("history"):
            self.full_history_for_status(trace_id, trace_events)
        else:
            self.latest_event_for_status(trace_id, trace_events)
