import os
import sys
import json
from prettytable import PrettyTable
import logging

log = logging.getLogger()


def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


# Create a output printer
#
# Formatting of output is defined in origocli/data/ouput-format.
# Each command defines what (from the API response) should be printed, and
# what the human-readable name should be
def create_output(format, configfile):
    datadir = f"{get_script_path()}/../origocli/data/output-format"
    filename = f"{datadir}/{configfile}"
    log.info(f"Creating output format: {format}, from: {filename}")
    with open(filename) as config_file:
        config = json.load(config_file)

    if format == "json":
        return JsonOutput(config)
    return TableOutput(config)


class TableOutput(PrettyTable):
    def __init__(self, config):
        self.config = config
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
            row_data.append(value)
        super().add_row(row_data)

    def add_rows(self, rows):
        for row in rows:
            self.add_row(row)
        self.align_rows()

    def align_rows(self):
        for key in self.config:
            name = self.config[key]["name"]
            self.align[name] = "l"


# TODO: merge many outputs to one array of elements when listing a version
class JsonOutput:
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
        return json.dumps(self.out)
