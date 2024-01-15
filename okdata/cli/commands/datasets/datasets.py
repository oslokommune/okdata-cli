import sys

from okdata.sdk.data.dataset import Dataset
from okdata.sdk.data.download import Download
from okdata.sdk.data.upload import Upload
from requests.exceptions import HTTPError

from okdata.cli.command import BaseCommand, BASE_COMMAND_OPTIONS
from okdata.cli.commands.datasets.wizards import DatasetCreateWizard
from okdata.cli.io import read_json, resolve_output_filepath
from okdata.cli.output import create_output


class DatasetsCommand(BaseCommand):
    __doc__ = f"""Oslo :: Datasets

Usage:
  okdata datasets ls [--filter=<filter> options]
  okdata datasets ls <uri> [options]
  okdata datasets cp <source> <target> [options]
  okdata datasets create [options]
  okdata datasets create-version <datasetid> [options]
  okdata datasets create-edition <datasetid> [<versionid>] [options]
  okdata datasets create-distribution <datasetid> [<versionid> <editionid>] [options]

Examples:
  okdata datasets ls
  okdata datasets ls --filter=bydelsfakta
  okdata datasets ls my-dataset
  okdata datasets ls my-dataset/1
  okdata datasets ls my-dataset/1/20240101T102030
  okdata datasets ls my-dataset/1/20240101T102030 --format=json
  okdata datasets create --file=dataset.json
  okdata datasets cp /tmp/file.csv ds:my-dataset-id

Options:{BASE_COMMAND_OPTIONS}
  --file=<file>             # Use this file for configuration or upload
  --prompt=<prompt>         # Use input prompt to collect data, default "no"
  --pipeline=<pipeline>     # Required when --prompt=no
    """

    def __init__(self):
        super().__init__(Dataset)
        self.download = Download(env=self.opt("env"))

    def handler(self):
        self.log.info("DatasetsCommand.handle()")
        if self.cmd("ls"):
            self.list_metadata()
        elif self.cmd("create"):
            if self.opt("file"):
                self.create_dataset()
            else:
                DatasetCreateWizard(self).start()
        elif self.cmd("cp"):
            self.copy_file()
        elif self.cmd("create-version"):
            self.create_version()
        elif self.cmd("create-edition"):
            self.create_edition()
        elif self.cmd("create-distribution"):
            self.create_distribution()
        else:
            self.help()

    def list_metadata(self):
        if self.arg("uri"):
            dataset_id, version, edition = self._dataset_components_from_uri(
                self.arg("uri"), auto_resolve=False
            )
            if edition:
                self.edition_information(dataset_id, version, edition)
            elif version:
                self.version_information(dataset_id, version)
            elif dataset_id:
                self.dataset(dataset_id)
        else:
            self.datasets()

    # #################################### #
    # Datasets
    # #################################### #
    def datasets(self):
        self.log.info("Listing datasets")
        dataset_list = self.sdk.get_datasets(filter=self.opt("filter"))
        out = create_output(self.opt("format"), "datasets_config.json")
        out.add_rows(dataset_list)
        self.print("Available datasets", out)

    def dataset(self, dataset_id):
        self.log.info(f"DatasetsCommand.handle_dataset({dataset_id})")

        dataset = self.sdk.get_dataset(dataset_id)
        versions = self.sdk.get_versions(dataset_id)
        latest = self._get_latest_version(dataset_id, False)

        if self.opt("format") == "json":
            self.print(
                "",
                {"dataset": dataset, "versions": versions, "latest": latest},
            )
            return

        out = create_output(self.opt("format"), "datasets_dataset_config.json")
        out.add_rows([dataset])
        self.print(f"Dataset: {dataset_id}", out)

        out = create_output(self.opt("format"), "datasets_dataset_versions_config.json")
        out.add_rows(versions)
        self.print(f"\nVersions available for: {dataset_id}", out)

        if latest:
            out.add_rows([latest])
            self.print(f"\nLatest version for: {dataset_id}", out)

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
    def version_information(self, dataset_id, version):
        self.log.info(f"Listing version for: {dataset_id}, {version}")

        editions = self.sdk.get_editions(dataset_id, version)
        out = create_output(self.opt("format"), "datasets_dataset_version_config.json")
        out.add_rows(editions)
        self.print(f"Editions available for: {dataset_id}, version: {version}", out)

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

    def _get_latest_version(self, dataset_id, exit_on_error=True):
        """Return the latest version of `dataset_id`.

        If there is no latest version, print an error message and exit if
        `exit_on_error` is true, otherwise return None.
        """
        try:
            return self.sdk.get_latest_version(dataset_id)
        except HTTPError as e:
            if e.response.status_code == 404:
                if exit_on_error:
                    sys.exit(
                        f"Version 'latest' not found for '{dataset_id}', "
                        "please specify the version ID."
                    )
                return None
            raise

    def resolve_or_load_versionid(self, dataset_id):
        self.log.info(f"Trying to resolve versionid for {dataset_id}")
        version_id = self.arg("versionid")
        if version_id is not None:
            self.log.info(f"Found version in arguments: {version_id}")
            return version_id
        latest_version = self._get_latest_version(dataset_id)
        self.log.info(
            f"Found version in latest dataset version: {latest_version['version']}"
        )
        return latest_version["version"]

    # #################################### #
    # Edition
    # #################################### #
    def edition_information(self, dataset_id, version, edition):
        self.log.info(f"Listing edition for: {dataset_id}, {version}, {edition}")

        edition_metadata = self.sdk.get_edition(dataset_id, version, edition)
        out = create_output(
            self.opt("format"), "datasets_dataset_version_edition_config.json"
        )
        out.add_rows([edition_metadata])
        self.print(out)
        distributions = self.sdk.get_distributions(dataset_id, version, edition)
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

    def resolve_or_create_edition(self, dataset_id, version_id):
        self.log.info(f"Trying to resolve edition for {version_id} on {dataset_id}")
        edition_id = self.arg("editionid")
        if edition_id is not None:
            self.log.info(f"Found edition in arguments: {edition_id}")
            return edition_id

        return self.sdk.auto_create_edition(dataset_id, version_id)

    def get_latest_or_create_edition(self, dataset_id, version):
        self.log.info(f"Resolving edition for dataset-uri: {dataset_id}/{version}")
        try:
            return self.sdk.get_latest_edition(dataset_id, version)
        except HTTPError as he:
            if he.response.status_code == 404:
                return self.sdk.auto_create_edition(dataset_id, version)
            raise

    # #################################### #
    # Distribution
    # #################################### #
    def create_distribution(self):
        payload = read_json(self.opt("file"))
        dataset_id = self.arg("datasetid")
        version_id = self.resolve_or_load_versionid(dataset_id)
        edition_id = self.resolve_or_create_edition(dataset_id, version_id)["Id"]
        edition = edition_id.split("/")[-1]
        self.log.info(f"Creating distribution for {edition_id} with payload: {payload}")

        distribution = self.sdk.create_distribution(
            dataset_id, version_id, edition, payload
        )
        self.print(f"Created distribution for {edition_id}", distribution)
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

    def _dataset_components_from_uri(
        self, dataset_uri, create_edition=False, auto_resolve=True
    ):
        """Return an ID/version/edition tuple given a dataset URI.

        Four different URI formats are supported:

        - {dataset_id}
        - {dataset_id}/{version}
        - {dataset_id}/{version}/latest
        - {dataset_id}/{version}/{edition}

        If `auto_resolve` is true, an attempt is made to resolve the version
        and edition even if they're not provided in the following ways:

        * If only a dataset ID is given, the latest version and edition is
          chosen. A new edition is created if `create_edition` is true, or if
          the latest version didn't already have any editions.

        * If only a dataset ID and version are given, the latest edition is
          chosen. A new edition is created if `create_edition` is true, or if
          the given version didn't already have any editions.

        * A specific dataset ID, version, and edition is chosen when all three
          components are provided. Given an edition with the special name
          'latest', the latest edition is chosen.

        Otherwise `None` is returned for missing parts.
        """
        parts = dataset_uri.split("/")
        dataset_id, version, edition = parts + [None] * (3 - len(parts))

        if auto_resolve:
            if not version:
                version = self._get_latest_version(dataset_id)["version"]

            if edition == "latest":
                edition = self.sdk.get_latest_edition(dataset_id, version)["Id"].split(
                    "/"
                )[-1]

            elif not edition:
                edition = (
                    self.sdk.auto_create_edition(dataset_id, version)
                    if create_edition
                    else self.get_latest_or_create_edition(dataset_id, version)
                )["Id"].split("/")[-1]

        return dataset_id, version, edition

    def upload_file(self, source, target):
        upload = Upload()
        dataset_id, version, edition = self._dataset_components_from_uri(target, True)

        self.log.info(f"Will upload file to: {dataset_id}/{version}/{edition})")

        try:
            res = upload.upload(source, dataset_id, version, edition, 3)
        except FileNotFoundError as e:
            sys.exit(e)

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

        summary = [f"Uploaded file to dataset: {dataset_id}", str(out)]
        if res["trace_id"]:
            summary += [
                "\nYou can watch the data processing status by running:\n",
                f"  okdata status {res['trace_id']} --watch",
            ]
        self.print("\n".join(summary))

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
