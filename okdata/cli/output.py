import inspect
import json
import logging
import os
from textwrap import wrap, fill

from prettytable import PrettyTable

log = logging.getLogger()


def get_script_path():
    return os.path.dirname(__file__)


# Create a output printer
#
# Formatting of output is defined in okdata/cli/data/ouput-format.
# Each command defines what (from the API response) should be printed, and
# what the human-readable name should be
def create_output(format, configfile):
    datadir = f"{get_script_path()}/data/output-format"
    filename = f"{datadir}/{configfile}"
    log.info(f"Creating output format: {format}, from: {filename}")
    with open(filename) as config_file:
        config = json.load(config_file)

    if format == "json":
        return JsonOutput(config)
    return TableOutput(config)


def table_config_from_schema(resource, exclude=None):
    if exclude is None:
        exclude = []

    def _for(properties):
        for property in properties:
            body = properties[property]
            if "properties" not in body:
                yield body["title"], {"name": body["title"], "key": property}
            else:
                _for(body["properties"])

    with open(
        os.path.dirname(inspect.getfile(resource))
        + f"/schemas/{resource.__resource_name__}.json",
        "r",
    ) as f:
        schema = json.loads(f.read())
        config = {
            key: body for key, body in _for(schema["properties"]) if key not in exclude
        }
        return TableOutput(config)


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
        value = ""
        for field in self.config[key]["fields"]:
            if field in row[row_key]:
                tmp = row[row_key][field]
                value += f"{tmp}\n"
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
        elif max_width and len(value) > max_width:
            value = fill(value, width=max_width)
        return value


# TODO: merge many outputs to one array of elements when listing a version
class JsonOutput:
    def __init__(self, config):
        self.config = config
        # set to True it will return a single object from self.out when printed. This will make it
        # easier to pass output to jq without having to access out[0] from the CLI
        self.output_singular_object = False
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

    def __repr__(self):
        return json.dumps(self.out)

    def __str__(self):
        if len(self.out) == 1 and self.output_singular_object is True:
            return json.dumps(self.out[0])
        return json.dumps(self.out)
