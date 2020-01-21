from origocli.command import BaseCommand
from origocli.output import create_output
from origocli.io import read_stdin_or_filepath
from origocli.date import (
    date_now,
    DATE_METADATA_EDITION_FORMAT,
)

from origo.data.dataset import Dataset
from origo.data.upload import Upload

import json


class DatasetsCommand(BaseCommand):
    """Oslo :: Datasets

    Usage:
      origo datasets ls [--format=<format> --env=<env> --filter=<filter>] [options]
      origo datasets ls <datasetid> [<versionid> <editionid>][--format=<format> --env=<env> options]
      origo datasets cp <filepath> <datasetid> [<versionid> <editionid> --format=<format> --env=<env> options]
      origo datasets create [--file=<file> --format=<format> --env=<env> options]
      origo datasets create-version <datasetid> [--file=<file> --format=<format> --env=<env> options]
      origo datasets create-edition <datasetid> [<versionid>] [--file=<file> --format=<format --env=<env> options]
      origo datasets create-distribution <datasetid> [<versionid> <editionid>] [--file=<file> --format=<format --env=<env> options]

    options:
      -h --help
      -d --debug
    """

    def __init__(self):
        super().__init__()
        env = self.opt("env")
        self.sdk = Dataset(env=env)
        self.sdk.login()
        self.handler = self.default

    # TODO: do a better mapping from rules to commands here...?
    def default(self):
        self.log.info("DatasetsCommand.handle()")
        if self.arg("datasetid") is None and self.cmd("ls") is True:
            self.datasets()
        elif self.arg("datasetid") is None and self.cmd("create") is True:
            self.create_dataset()
        elif self.cmd("cp") is True:
            self.copy_file()
        elif (
            self.arg("datasetid") is not None
            and self.cmd("create-distribution") is True
        ):
            self.create_distribution()
        elif self.arg("datasetid") is not None and self.cmd("create-edition") is True:
            self.create_edition()
        elif self.arg("datasetid") is not None and self.cmd("create-version") is True:
            self.create_version()
        elif self.arg("editionid") is not None or self.opt("editionid") is not None:
            self.edition_information()
        elif self.arg("versionid") is not None or self.opt("versionid") is not None:
            self.version()
        elif self.arg("datasetid") is not None:
            self.dataset()
        else:
            BaseCommand.help()

    # #################################### #
    # Datasets
    # #################################### #
    def datasets(self):
        try:
            self.log.info("Listing datasets")
            datset_list = self.sdk.get_datasets(filter=self.opt("filter"))
            out = create_output(self.opt("format"), "datasets_config.json")
            out.add_rows(datset_list)
            self.print("Available datasets", out)
        except Exception as e:
            self.log.exception(f"Failed badly: {e}")

    def dataset(self):
        dataset_id = self.arg("datasetid")
        self.log.info(f"DatasetsCommand.handle_dataset({dataset_id})")
        try:
            set = self.sdk.get_dataset(dataset_id)
            versions = self.sdk.get_versions(dataset_id)
            latest = self.sdk.get_latest_version(dataset_id)
            if self.opt("format") == "json":
                list = {}
                list["dataset"] = set
                list["versions"] = versions
                list["latest"] = latest
                self.print("", json.dumps(list))
                return

            out = create_output(self.opt("format"), "datasets_dataset_config.json")
            out.add_rows([set])
            self.print(f"Dataset: {dataset_id}", out)

            self.print(f"\n\nVersions available for: {dataset_id}")
            out = create_output(
                self.opt("format"), "datasets_dataset_versions_config.json"
            )
            out.add_rows(versions)
            self.print(f"\n\nVersions available for: {dataset_id}", out)

            out = create_output(
                self.opt("format"), "datasets_dataset_versions_config.json"
            )
            out.add_rows([latest])
            self.print(f"\n\nLatest version for: {dataset_id}", out)
        except Exception as e:
            self.log.exception(f"Failed badly: {e}")

    def create_dataset(self):
        payload = read_stdin_or_filepath(self.opt("file"))
        self.log.info(f"Creating dataset with payload: {payload}")
        try:
            dataset = self.sdk.create_dataset(payload)
            dataset_id = dataset["Id"]
            self.log.info(f"Created dataset with id: {dataset_id}")
            self.print(f"Created dataset: {dataset_id}", dataset)
        except Exception as e:
            self.log.exception(f"Failed badly: {e}")

    # #################################### #
    # Version
    # #################################### #
    def version(self):
        if self.cmd("create-edition") is not False:
            self.create_version()
        else:
            self.version_information()

    def version_information(self):
        dataset_id = self.arg("datasetid")
        version_id = self.arg("versionid") or self.opt("versionid")
        self.log.info(f"Listing version for: {dataset_id}, {version_id}")
        try:
            editions = self.sdk.get_editions(dataset_id, version_id)
            out = create_output(
                self.opt("format"), "datasets_dataset_version_config.json"
            )
            out.add_rows(editions)
            self.print(
                f"Editions available for: {dataset_id}, version: {version_id}", out
            )
        except Exception as e:
            self.log.exception(f"Failed badly: {e}")

    def create_version(self):
        dataset_id = self.arg("datasetid")
        payload = read_stdin_or_filepath(self.opt("file"))
        self.log.info(
            f"Creating version for dataset: {dataset_id} with payload: {payload}"
        )
        try:
            version = self.sdk.create_version(dataset_id, payload)
            version_id = version["Id"]
            self.log.info(f"Created version: {version_id} on dataset: {dataset_id}")
            self.print(f"Created version: {version_id}", version)
        except Exception as e:
            self.log.exception(f"Failed badly: {e}")

    def resolve_or_load_versionid(self, dataset_id):
        self.log.info(f"Trying to resolve versionid for {dataset_id}")
        version_id = self.arg("versionid") or self.opt("versionid")
        if version_id is not None:
            self.log.info(f"Found version in arguments: {version_id}")
            return version_id
        latest_version = self.sdk.get_latest_version(dataset_id)
        self.log.info(
            f"Found version in latest dataset version: {latest_version['version']}"
        )
        return latest_version["version"]

    # #################################### #
    # Edition
    # #################################### #
    def edition_information(self):
        dataset_id = self.arg("datasetid")
        version_id = self.arg("versionid") or self.opt("versionid")
        edition_id = self.arg("editionid") or self.opt("editionid")
        self.log.info(f"Listing edition for: {dataset_id}, {version_id}, {edition_id}")
        try:
            edition = self.sdk.get_edition(dataset_id, version_id, edition_id)
            out = create_output(
                self.opt("format"), "datasets_dataset_version_edition_config.json"
            )
            out.add_rows([edition])
            print(out)
            distributions = self.sdk.get_distributions(
                dataset_id, version_id, edition_id
            )
            out = create_output(
                self.opt("format"),
                "datasets_dataset_version_edition_distributions_config.json",
            )
            out.add_rows(distributions)
            self.print("Files available: ", out)
        except Exception as e:
            self.log.exception(f"Failed: {e}")

    def create_edition(self):
        payload = read_stdin_or_filepath(self.opt("file"))
        dataset_id = self.arg("datasetid")
        version_id = self.resolve_or_load_versionid(dataset_id)
        self.log.info(
            f"Creating edition for {version_id} on {dataset_id} with payload: {payload}"
        )
        try:
            edition = self.sdk.create_edition(dataset_id, version_id, payload)
            self.print(f"Created edition for {version_id} on {dataset_id}", edition)
            return edition
        except Exception as e:
            self.log.exception(f"Failed badly: {e}")

    def resolve_or_create_edition(self, dataset_id, version_id):
        self.log.info(f"Trying to resolve edition for {version_id} on {dataset_id}")
        edition_id = self.arg("editionid") or self.opt("editionid")
        if edition_id is not None:
            self.log.info(f"Found edition in arguments: {edition_id}")
            return edition_id

        description = f"Auto-created edition for {dataset_id}/{version_id}"
        now = date_now()
        data = {
            "edition": now.strftime(DATE_METADATA_EDITION_FORMAT),
            "description": description,
        }
        self.log.info(
            f"Creating new edition for: {dataset_id}/{version_id} with data: {data}"
        )

        edition = self.sdk.create_edition(dataset_id, version_id, data)
        self.log.info(f"Created edition: {edition}")
        (_, _, edition_id) = edition["Id"].split("/")
        self.log.info(f"returning: {edition_id}")
        return edition_id

    # #################################### #
    # Distribution
    # #################################### #
    def create_distribution(self):
        payload = read_stdin_or_filepath(self.opt("file"))
        dataset_id = self.arg("datasetid")
        version_id = self.resolve_or_load_versionid(dataset_id)
        edition_id = self.resolve_or_create_edition(dataset_id, version_id)
        self.log.info(
            f"Creating distribution for {edition_id} on {dataset_id}/{version_id} with payload: {payload}"
        )
        try:
            distribution = self.sdk.create_distribution(
                dataset_id, version_id, edition_id, payload
            )
            self.print(
                f"Created distribution for {version_id} on {dataset_id}", distribution
            )
            return distribution
        except Exception as e:
            self.log.exception(f"Failed badly: {e}")

    # #################################### #
    # File handling
    # #################################### #
    def copy_file(self):
        # TODO: check for "ds:" position
        (ns, dataset_id) = self.arg("datasetid").split(":")
        self.log.info(f"Copying file to dataset: {dataset_id}")
        version_id = self.resolve_or_load_versionid(dataset_id)
        edition_id = self.resolve_or_create_edition(dataset_id, version_id)
        try:
            upload = Upload()
            self.log.info(
                f"Will copy file to: {dataset_id}, {version_id}, {edition_id})"
            )
            res = upload.upload(
                self.arg("filepath"), dataset_id, version_id, edition_id
            )
            self.log.info(f"Upload returned: {res}")
            self.print_success("Uploaded file")
        except Exception as e:
            self.log.exception(f"Failed: {e}")
