import json
from origocli.command import BaseCommand
from origo.elasticsearch.queries import ElasticsearchQueries, NotDatasetOwnerError


class ElasticsearchQueryCommand(BaseCommand):
    """
    Oslo :: Elasticsearch queries

    usage:
        origo esq eventstat <datasetid> [options]

    Options:
        -d --debug
        --format=<format>
    """

    def __init__(self):
        super().__init__()
        env = self.opt("env")
        self.sdk = ElasticsearchQueries(env=env)
        self.sdk.login()
        self.handler = self.default

    def default(self):
        try:
            dataset_id = self.arg("datasetid")
            if self.cmd("eventstat"):
                self.event_stat(dataset_id)
        except NotDatasetOwnerError:
            self.print(f"You are not the owner of: {dataset_id}")
        except Exception as e:
            self.log.exception("Failed", e)
            self.print(f"Operation failed: {repr(e)}")

    def event_stat(self, dataset_id):
        data = self.sdk.event_stat(dataset_id)

        last_hour = data["last_hour"]["events"]
        last_day = data["last_day"]["events"]
        last_week = data["last_week"]["events"]

        payload = None
        if self.opt("format") == "json":
            payload = json.dumps(data)

        self.print("Events ...")
        self.print("Last hour\tLast day\tLast week")
        self.print(f"{last_hour}\t\t{last_day}\t\t{last_week}", payload)
