from time import sleep

from okdata.sdk.status import Status

from okdata.cli.command import BaseCommand, BASE_COMMAND_OPTIONS
from okdata.cli.output import create_output


class StatusCommand(BaseCommand):
    __doc__ = f"""Oslo :: Status

Usage:
  okdata status <trace_id> [options]

Examples:
  okdata status trace-id-from-system
  okdata status trace-id-from-system --watch
  okdata status trace-id-from-system --history
  okdata status trace-id-from-system --format=json | jq ".done"

Options:{BASE_COMMAND_OPTIONS}
  --history
  --watch
    """

    def __init__(self):
        super().__init__(Status)

    def login(self):
        self.sdk.login()

    def handler(self):
        self.log.info("StatusCommand.handler()")
        if self.arg("trace_id"):
            self.status_for_id(self.arg("trace_id"))
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

    def get_trace_events(self, trace_id):
        self.log.info(f"Looking up status: {trace_id}")
        trace_events = self.sdk.get_status(trace_id)
        return StatusCommand.get_error_messages(trace_events)

    def wait_until_done(self, trace_id):
        """Wait until status for `trace_id` is ready, then return the trace."""
        trace_events = self.get_trace_events(trace_id)
        trace_status = StatusCommand.find_latest_event(trace_events)["trace_status"]

        if trace_status != "FINISHED":
            print("Waiting for processing to finish", end="", flush=True)

        while trace_status != "FINISHED":
            print(".", end="", flush=True)
            sleep(2)
            trace_events = self.get_trace_events(trace_id)
            trace_status = StatusCommand.find_latest_event(trace_events)["trace_status"]
        print()

        return trace_events

    def status_for_id(self, trace_id):
        trace_events = (
            self.wait_until_done(trace_id)
            if self.opt("watch")
            else self.get_trace_events(trace_id)
        )

        if self.opt("history"):
            self.full_history_for_status(trace_id, trace_events)
        else:
            self.latest_event_for_status(trace_id, trace_events)
