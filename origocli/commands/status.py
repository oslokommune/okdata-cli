from origocli.command import BaseCommand
from origocli.output import create_output

from origo.status import Status


class StatusCommand(BaseCommand):
    """Oslo :: Status

    Usage:
      origo status <statusid> [options --history]

    Get the status of a process in origo
        Add --history to get the full history of the status ID
        To get a true/false value from the statusid: `origo status <statusid> --format=json | jq ".done"`

    Options:
      -d --debug
      --format=<format>
    """

    def __init__(self):
        super().__init__()
        env = self.opt("env")
        self.sdk = Status(env)
        self.handler = self.default

    def login(self):
        self.sdk.login()

    def default(self):
        self.log.info("StatusCommand.default()")
        if self.arg("statusid"):
            self.status_for_id()
        else:
            self.print("Invalid command")

    def add_status_for_id_rows(self, out, statusid, statuses):
        finished = False
        # Note: Values here come from common-python
        run_status = "STARTED"
        status = "OK"
        for el in statuses:
            if el["run_status"] == "FINISHED":
                el["done"] = False
                if el["status"] == "OK":
                    el["done"] = True
                    finished = True
                out.add_row(el)
            else:
                # Check against baseline values:
                if el["run_status"] != "STARTED":
                    run_status = el["run_status"]
                if el["status"] != "OK":
                    status = el["status"]

        if not finished:
            out.add_row(
                {
                    "done": False,
                    "id": statusid,
                    "run_status": run_status,
                    "status": status,
                }
            )

    def full_history_for_status(self, statusid, statuses):
        if len(statuses) > 0:
            out = create_output(self.opt("format"), "status_history_config.json")
            out.add_rows(statuses)
            self.print(f"Status for: {statusid}", out)
        else:
            self.print(
                f"No history found for status",
                {"error": 1, "message": "No statuses found"},
            )

    def status_for_id(self):
        statusid = self.arg("statusid")
        self.log.info(f"Looking up status: {statusid}")
        statuses = self.sdk.get_status(statusid)
        if self.opt("history"):
            self.full_history_for_status(statusid, statuses)
        else:
            out = create_output(self.opt("format"), "status_config.json")
            out.output_singular_object = True
            self.add_status_for_id_rows(out, statusid, statuses)
            self.print(f"Status for: {statusid}", out)
