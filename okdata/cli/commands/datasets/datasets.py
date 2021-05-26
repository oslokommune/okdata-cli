from okdata.sdk.data.dataset import Dataset
from okdata.sdk.data.download import Download
from okdata.sdk.data.upload import Upload
from requests.exceptions import HTTPError

from okdata.cli.command import BaseCommand, BASE_COMMAND_OPTIONS
from okdata.cli.commands.datasets import DatasetsBoilerplateCommand
from okdata.cli.commands.datasets.wizards import DatasetCreateWizard
from okdata.cli.date import date_now, DATE_METADATA_EDITION_FORMAT
from okdata.cli.io import read_json, resolve_output_filepath
from okdata.cli.output import create_output


class DatasetsCommand(BaseCommand):
    __doc__ = f"""Oslo :: Datasets

Usage:
  okdata datasets ls [--format=<format>  --env=<env> --filter=<filter> options]
  okdata datasets ls <datasetid> [<versionid> <editionid>][--format=<format> --env=<env> options]
  okdata datasets cp <source> <target> [--format=<format> --env=<env> options]
  okdata datasets create [--file=<file> --format=<format> --env=<env> options]
  okdata datasets create-version <datasetid> [--file=<file> --format=<format> --env=<env> options]
  okdata datasets create-edition <datasetid> [<versionid>] [--file=<file> --format=<format> --env=<env> options]
  okdata datasets create-distribution <datasetid> [<versionid> <editionid>] [--file=<file> --format=<format> --env=<env> options]
  okdata datasets boilerplate <name> [--file=<file> --prompt=<prompt> --pipeline=<pipeline> options]

Examples:
  okdata datasets ls --filter=bydelsfakta
  okdata datasets ls --filter=bydelsfakta --format=json
  okdata datasets create --file=dataset.json
  okdata datasets cp /tmp/file.csv ds:my-dataset-id
  okdata datasets boilerplate oslo-traffic-data
  okdata datasets boilerplate oslo-traffic-data --file=/tmp/initial-file.csv
  okdata datasets boilerplate oslo-traffic-data --pipeline=data-copy --prompt=no
  okdata datasets boilerplate geodata-from-my-iot-devices

Options:{BASE_COMMAND_OPTIONS}
  --file=<file>             # Use this file for configuration or upload
  --prompt=<prompt>         # Use input prompt to collect data, default "no"
  --pipeline=<pipeline>     # Required when --prompt=no
    """

    def __init__(self):
        super().__init__()
        env = self.opt("env")
        self.sdk = Dataset(env=env)
        self.download = Download(env=env)
        self.handler = self.default
        self.sub_commands = [DatasetsBoilerplateCommand]

    # TODO: do a better mapping from rules to commands here...?
    def default(self):
        self.log.info("DatasetsCommand.handle()")
        if self.arg("datasetid") is None and self.cmd("ls") is True:
            self.datasets()
        elif self.arg("datasetid") is None and self.cmd("create") is True:
            if self.opt("file"):
                self.create_dataset()
            else:
                DatasetCreateWizard(self).start()
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
        self.log.info("Listing datasets")
        dataset_list = self.sdk.get_datasets(filter=self.opt("filter"))
        out = create_output(self.opt("format"), "datasets_config.json")
        out.add_rows(dataset_list)
        self.print("Available datasets", out)

    def dataset(self):
        dataset_id = self.arg("datasetid")
        self.log.info(f"DatasetsCommand.handle_dataset({dataset_id})")

        set = self.sdk.get_dataset(dataset_id)
        versions = self.sdk.get_versions(dataset_id)
        latest = self.sdk.get_latest_version(dataset_id)
        if self.opt("format") == "json":
            list = {}
            list["dataset"] = set
            list["versions"] = versions
            list["latest"] = latest
            self.print("", list)
            return

        out = create_output(self.opt("format"), "datasets_dataset_config.json")
        out.add_rows([set])
        self.print(f"Dataset: {dataset_id}", out)

        out = create_output(self.opt("format"), "datasets_dataset_versions_config.json")
        out.add_rows(versions)
        self.print(f"\n\nVersions available for: {dataset_id}", out)

        out = create_output(self.opt("format"), "datasets_dataset_versions_config.json")
        out.add_rows([latest])

        self.print(f"\n\nLatest version for: {dataset_id}", out)

    def create_dataset(self):
        payload = read_json(self.opt("file"))
        self.log.info(f"Creating dataset with payload: {payload}")

        dataset = self.sdk.create_dataset(payload)
        dataset_id = dataset["Id"]
        self.log.info(f"Created dataset with id: {dataset_id}")
        self.print(f"Created dataset: {dataset_id}", dataset)

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

        editions = self.sdk.get_editions(dataset_id, version_id)
        out = create_output(self.opt("format"), "datasets_dataset_version_config.json")
        out.add_rows(editions)
        self.print(f"Editions available for: {dataset_id}, version: {version_id}", out)

    def create_version(self):
        dataset_id = self.arg("datasetid")
        payload = read_json(self.opt("file"))
        self.log.info(
            f"Creating version for dataset: {dataset_id} with payload: {payload}"
        )

        version = self.sdk.create_version(dataset_id, payload)
        version_id = version["Id"]
        self.log.info(f"Created version: {version_id} on dataset: {dataset_id}")
        self.print(f"Created version: {version_id}", version)

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

        edition = self.sdk.get_edition(dataset_id, version_id, edition_id)
        out = create_output(
            self.opt("format"), "datasets_dataset_version_edition_config.json"
        )
        out.add_rows([edition])
        print(out)
        distributions = self.sdk.get_distributions(dataset_id, version_id, edition_id)
        out = create_output(
            self.opt("format"),
            "datasets_dataset_version_edition_distributions_config.json",
        )
        out.add_rows(distributions)
        self.print("Files available: ", out)

    def create_edition(self):
        payload = read_json(self.opt("file"))
        dataset_id = self.arg("datasetid")
        version_id = self.resolve_or_load_versionid(dataset_id)
        self.log.info(
            f"Creating edition for {version_id} on {dataset_id} with payload: {payload}"
        )

        edition = self.sdk.create_edition(dataset_id, version_id, payload)
        self.print(f"Created edition for {version_id} on {dataset_id}", edition)
        return edition

    def _auto_create_edition(self, dataset_id, version_id):
        """Auto-create a new edition for the given dataset version.

        Return the ID of the newly created edition.
        """
        data = {
            "edition": date_now().strftime(DATE_METADATA_EDITION_FORMAT),
            "description": f"Auto-created edition for {dataset_id}/{version_id}",
        }

        self.log.info(
            f"Creating new edition for {dataset_id}/{version_id} with data: {data}"
        )
        edition = self.sdk.create_edition(dataset_id, version_id, data)
        self.log.info(f"Created edition: {edition}")

        return edition["Id"].split("/")[-1]

    def resolve_or_create_edition(self, dataset_id, version_id):
        self.log.info(f"Trying to resolve edition for {version_id} on {dataset_id}")
        edition_id = self.arg("editionid") or self.opt("editionid")
        if edition_id is not None:
            self.log.info(f"Found edition in arguments: {edition_id}")
            return edition_id

        return self._auto_create_edition(dataset_id, version_id)

    def get_latest_or_create_edition(self, dataset_id, version):
        self.log.info(f"Resolving edition for dataset-uri: {dataset_id}/{version}")
        try:
            return self.sdk.get_latest_edition(dataset_id, version)["Id"].split("/")[-1]
        except HTTPError as he:
            if he.response.status_code == 404:
                return self._auto_create_edition(dataset_id, version)
            else:
                raise he

    # #################################### #
    # Distribution
    # #################################### #
    def create_distribution(self):
        payload = read_json(self.opt("file"))
        dataset_id = self.arg("datasetid")
        version_id = self.resolve_or_load_versionid(dataset_id)
        edition_id = self.resolve_or_create_edition(dataset_id, version_id)
        self.log.info(
            f"Creating distribution for {edition_id} on {dataset_id}/{version_id} with payload: {payload}"
        )

        distribution = self.sdk.create_distribution(
            dataset_id, version_id, edition_id, payload
        )
        self.print(
            f"Created distribution for {version_id} on {dataset_id}", distribution
        )
        return distribution

    # #################################### #
    # File handling
    # #################################### #
    def copy_file(self):
        source = self.arg("source")
        target = self.arg("target")

        if source.startswith("ds:") and target.startswith("ds:"):
            self.log.error("Copying between datasets isn't supported yet.")
        elif target.startswith("ds:"):
            self.upload_file(source, target[3:])
        elif source.startswith("ds:"):
            self.download_files(source[3:], target)
        else:
            self.log.error(
                "Either source or target needs to be a dataset (prefixed with 'ds:')."
            )

    def _dataset_components_from_uri(self, dataset_uri, create_edition=False):
        """Return an ID/version/edition tuple given a dataset URI.

        Four different URI formats are supported:

        - {dataset_id}
        - {dataset_id}/{version}
        - {dataset_id}/{version}/latest
        - {dataset_id}/{version}/{edition}

        If only a dataset ID is given, the latest version and edition is
        chosen. A new edition is created if `create_edition` is true, or if the
        latest version didn't already have any editions.

        If only a dataset ID and version are given, the latest edition is
        chosen. A new edition is created if `create_edition` is true, or if the
        given version didn't already have any editions.

        A specific dataset ID, verison, and edition is chosen when all three
        components are provided. Given an edition with the special name
        'latest', the latest edition is chosen.
        """
        parts = dataset_uri.split("/")
        dataset_id, version, edition = parts + [None] * (3 - len(parts))

        if not version:
            version = self.sdk.get_latest_version(dataset_id)["version"]

        if edition == "latest":
            edition = self.sdk.get_latest_edition(dataset_id, version)["Id"].split("/")[
                -1
            ]

        elif not edition:
            edition = (
                self._auto_create_edition(dataset_id, version)
                if create_edition
                else self.get_latest_or_create_edition(dataset_id, version)
            )

        return dataset_id, version, edition

    def upload_file(self, source, target):
        upload = Upload()
        dataset_id, version, edition = self._dataset_components_from_uri(target, True)

        self.log.info(f"Will upload file to: {dataset_id}/{version}/{edition})")
        res = upload.upload(source, dataset_id, version, edition, 3)
        self.log.info(f"Upload returned: {res}")

        out = create_output(self.opt("format"), "datasets_copy_file_config.json")
        out.output_singular_object = True
        data = {
            "dataset": dataset_id,
            "file": source,
            "uploaded": res["result"],
            "trace_id": res["trace_id"],
        }
        out.add_row(data)
        self.print(f"Uploaded file to dataset: {dataset_id}", out)

    def download_files(self, source, target):
        dataset_id, version, edition = self._dataset_components_from_uri(source)
        downloaded_files = self.download.download(
            dataset_id, version, edition, resolve_output_filepath(target)
        )
        self.log.info(f"Download returned: {downloaded_files}")
        out = create_output(self.opt("format"), "datasets_copy_file_config_2.json")
        out.output_singular_object = True
        data = {
            "source": f"ds:{'/'.join([dataset_id, version, edition])}",
            "target": "\n".join(downloaded_files["files"]),
            "trace_id": "n/a",
        }
        out.add_row(data)
        self.print(f"Downloaded files from dataset: {dataset_id}", out)
