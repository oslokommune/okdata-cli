from origocli.command import BaseCommand, BASE_COMMAND_OPTIONS
from origocli.output import create_output

from origo.status import Status


class StatusCommand(BaseCommand):
    __doc__ = f"""Oslo :: Status

Usage:
  origo status <statusid> [options --history]

Examples:
  origo status status-id-from-system
  origo status status-id-from-system --format=json | jq ".done"
  origo status status-id-from-system --history

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
        if self.arg("statusid"):
            self.status_for_id()
        else:
            self.print("Invalid command")

    @staticmethod
    def add_status_for_id_rows(out, statusid, statuses):
        finished = False
        run_status = statuses[-1]["run_status"]
        status = statuses[-1]["status"]
        for el in statuses:
            if el["run_status"] == "FINISHED":
                el["done"] = False
                if el["status"] == "OK":
                    el["done"] = True
                    finished = True
                out.add_row(el)

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
        if statuses:
            out = create_output(self.opt("format"), "status_history_config.json")
            out.add_rows(statuses)
            self.print(f"Status for: {statusid}", out)
        else:
            self.print(
                "No history found for status",
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
            StatusCommand.add_status_for_id_rows(out, statusid, statuses)
            self.print(f"Status for: {statusid}", out)
