import csv
import io
import json
import logging
import os
from datetime import datetime
from textwrap import wrap, fill

from prettytable import PrettyTable

log = logging.getLogger()


def _get_script_path():
    return os.path.dirname(__file__)


def create_output(fmt, config_file):
    """Create and return an output printer.

    Formatting of output is defined in the `okdata/cli/data/ouput-format`
    directory. Each command defines which fields from the API response should
    be printed, and what the human-readable name should be.
    """
    datadir = f"{_get_script_path()}/data/output-format"
    filename = f"{datadir}/{config_file}"
    log.info(f"Creating output format: {fmt}, from: {filename}")

    with open(filename) as f:
        config = json.load(f)

    return {
        "json": JsonOutput(config),
        "csv": CSVOutput(config),
    }.get(fmt, TableOutput(config))


class TableOutput(PrettyTable):
    def __init__(self, config):
        self.config = config
        self.output_singular_object = False
        column_headers = []
        for key in self.config:
            name = self.config[key]["name"]
            column_headers.append(name)
        super().__init__(column_headers)

    def field_values(self, row, row_key, key):
        values = []
        for field in self.config[key]["fields"]:
            if field in row[row_key]:
                values.append(str(row[row_key][field]))
        return "\n".join(values)

    def get_row_value(self, row, key):
        row_key = self.config[key]["key"]
        if row_key in row:
            if "fields" in self.config[key]:
                return self.field_values(row, row_key, key)
            if row[row_key] is not None:
                return row[row_key]
        return "N/A"

    def add_row(self, row):
        row_data = []
        for key in self.config:
            value = self.get_row_value(row, key)
            max_width = self.config[key].get("wrap")
            value = TableOutput.format_cell_value(value, max_width)
            row_data.append(value)
        super().add_row(row_data)
        self.align_rows()

    def add_rows(self, rows):
        for row in rows:
            self.add_row(row)
        self.align_rows()

    def align_rows(self):
        for key in self.config:
            name = self.config[key]["name"]
            self.align[name] = "l"

    @staticmethod
    def format_cell_value(value, max_width):
        try:
            dt = datetime.fromisoformat(value)
            if dt.tzinfo:
                return dt.astimezone().isoformat(timespec="seconds")
        except (TypeError, ValueError):
            pass

        if isinstance(value, list) and len(value) == 1:
            value = str(value[0])

        if isinstance(value, list):
            value = [str(v) for v in value]
            if max_width:
                value = [
                    "\n  ".join(wrap(v, width=max_width)) if len(v) > max_width else v
                    for v in value
                ]
            value = ["- " + v for v in value]
            value = "  \n".join(value)
        elif isinstance(value, bool):
            value = "Yes" if value else "No"
        elif max_width and len(value) > max_width:
            value = fill(value, width=max_width)
        return value


class StructuredDataOutput:
    def __init__(self, config):
        self.config = config
        self.out = []

    def field_values(self, row, row_key, key):
        value = {}
        for field in self.config[key]["fields"]:
            value[field] = "N/A"
            if field in row[row_key]:
                tmp = row[row_key][field]
                value[field] = tmp
        return value

    def get_row_value(self, row, key):
        value = "N/A"
        row_key = self.config[key]["key"]
        if row_key in row:
            if "fields" in self.config[key]:
                value = self.field_values(row, row_key, key)
            else:
                value = row[row_key]
        return value

    def add_row(self, row):
        row_data = {}
        for key in self.config:
            value = self.get_row_value(row, key)
            row_key = self.config[key]["key"]
            row_data[row_key] = value
        self.out.append(row_data)

    def add_rows(self, rows):
        for row in rows:
            self.add_row(row)

    def __str__(self):
        raise NotImplementedError


class CSVOutput(StructuredDataOutput):
    def __str__(self):
        out = io.StringIO()
        writer = csv.DictWriter(out, self.out[0].keys())
        writer.writeheader()
        writer.writerows(self.out)
        return out.getvalue()

    def get_row_value(self, row, key):
        val = super().get_row_value(row, key)

        if isinstance(val, str):
            return val.replace("\n", "")
        elif isinstance(val, list):
            return ";".join(val)
        return val


# TODO: merge many outputs to one array of elements when listing a version
class JsonOutput(StructuredDataOutput):
    def __init__(self, config):
        super().__init__(config)
        # set to True it will return a single object from self.out when printed. This will make it
        # easier to pass output to jq without having to access out[0] from the CLI
        self.output_singular_object = False

    def __repr__(self):
        return json.dumps(self.out)

    def __str__(self):
        if len(self.out) == 1 and self.output_singular_object is True:
            return json.dumps(self.out[0])
        return json.dumps(self.out)
