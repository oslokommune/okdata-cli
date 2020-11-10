from datetime import datetime

import pytest
from okdata.sdk.data.dataset import Dataset

from conftest import set_argv
from okdata.cli.commands.datasets import DatasetsCommand
from okdata.cli.output import TableOutput

DATASETS_CMD_QUAL = f"{DatasetsCommand.__module__}.{DatasetsCommand.__name__}"
DATASETS_QUAL = f"{Dataset.__module__}.{Dataset.__name__}"

dataset = {
    "theme": ["Befolkning og samfunn", "Helse"],
    "publisher": "BBJ (Bydel Bjerke)",
    "confidentiality": "green",
    "frequency": "Uregelmessig",
    "keywords": [],
    "contactPoint": {"email": "test@test.test"},
    "description": "asdasdasd",
    "Id": "autorisasjon-test-jd",
    "Type": "Dataset",
    "title": "autorisasjon-test-jd",
    "_links": {"self": {"href": "/datasets/autorisasjon-test-jd"}},
}

version = {"version": "1"}

edition_id = datetime.now().isoformat()
edition = {
    "Id": f"{dataset['Id']}/{version['version']}/{edition_id}",
    "edition": edition_id,
}


@pytest.fixture()
def output(mocker):
    return mocker.spy(TableOutput, "add_rows")


def output_with_argument(output, argument):
    for (args, kwargs) in output.call_args_list:
        if argument in args:
            return True
    return False


def create_cmd(mocker, *args):
    set_argv("datasets", *args)
    cmd = DatasetsCommand()
    mocker.patch.object(cmd, "sdk")
    mocker.patch.object(cmd, "log")

    cmd.sdk.get_datasets.return_value = [dataset, dataset]
    cmd.sdk.get_dataset.return_value = dataset
    cmd.sdk.get_latest_version.return_value = version
    cmd.sdk.get_versions.return_value = [version]

    edition2 = edition.copy()
    edition2["edition"] = datetime.now().isoformat()
    new_edition = edition.copy()
    new_edition["Id"] = f"{dataset['Id']}/{version['version']}/new-edition"
    cmd.sdk.get_editions.return_value = [edition, edition2]
    cmd.sdk.get_edition.return_value = edition
    cmd.sdk.get_latest_edition.return_value = edition
    cmd.sdk.create_edition.return_value = new_edition
    return cmd


class TestDatasetsLs:
    def test_datasets(self, mock_print, mocker, output):
        cmd = create_cmd(mocker, "ls")
        cmd.handler()
        assert output_with_argument(output, [dataset, dataset])
        assert mock_print.called_once

    def test_dataset(self, mock_print, mocker, output):
        cmd = create_cmd(mocker, "ls", dataset["Id"])
        cmd.handler()

        assert output_with_argument(output, [dataset])
        assert mock_print.called_once
        assert cmd.sdk.get_dataset.called
        assert cmd.sdk.get_versions.called
        assert cmd.sdk.get_latest_version.called
        assert not cmd.log.exception.called

    def test_dataset_format_json(self, mocker, mock_print):
        cmd = create_cmd(mocker, "ls", dataset["Id"], "--format", "json")
        cmd.handler()
        mock_print.assert_called_once_with(
            "", {"dataset": dataset, "versions": [version], "latest": version}
        )
        assert cmd.sdk.get_dataset.called
        assert cmd.sdk.get_versions.called
        assert cmd.sdk.get_latest_version.called
        assert not cmd.log.exception.called

    def test_version(self, mocker, output):
        cmd = create_cmd(mocker, "ls", dataset["Id"], version["version"])
        cmd.handler()
        assert output_with_argument(output, cmd.sdk.get_editions.return_value)

    def test_edition(self, mocker, output):
        cmd = create_cmd(
            mocker, "ls", dataset["Id"], version["version"], edition["edition"]
        )
        cmd.handler()
        assert output_with_argument(output, [edition])


class TestDatasetsCp:
    def test_copy_local_files(self, mocker):
        cmd = create_cmd(mocker, "cp", "foo", "bar")
        mocker.patch.object(cmd, "upload_file")
        mocker.patch.object(cmd, "download_files")
        cmd.handler()
        assert not cmd.upload_file.called
        assert not cmd.download_files.called

    def test_copy_upload(self, mocker):
        cmd = create_cmd(mocker, "cp", "foo", "ds:bar")
        mocker.patch.object(cmd, "upload_file")
        mocker.patch.object(cmd, "download_files")
        cmd.handler()
        cmd.upload_file.assert_called_once_with("foo", "bar")
        assert not cmd.download_files.called

    def test_copy_download(self, mocker):
        cmd = create_cmd(mocker, "cp", "ds:foo", "bar")
        mocker.patch.object(cmd, "upload_file")
        mocker.patch.object(cmd, "download_files")
        cmd.handler()
        assert not cmd.upload_file.called
        cmd.download_files.assert_called_once_with("foo", "bar")

    def test_copy_between_datasets(self, mocker):
        cmd = create_cmd(mocker, "cp", "ds:foo", "ds:bar")
        mocker.patch.object(cmd, "upload_file")
        mocker.patch.object(cmd, "download_files")
        cmd.handler()
        assert not cmd.upload_file.called
        assert not cmd.download_files.called


class TestUtils:
    def test_auto_create_edition(self, mocker):
        cmd = create_cmd(mocker, "ls")
        assert (
            cmd._auto_create_edition(dataset["Id"], version["version"]) == "new-edition"
        )

    def test_dataset_components_from_uri_only_ds(self, mocker):
        cmd = create_cmd(mocker, "ls")
        dataset_id, _version, _edition = cmd._dataset_components_from_uri(dataset["Id"])
        assert dataset_id == dataset["Id"]
        assert _version == version["version"]
        assert _edition == edition["edition"]

    def test_dataset_components_from_uri_ds_and_version(self, mocker):
        cmd = create_cmd(mocker, "ls")
        dataset_id, _version, _edition = cmd._dataset_components_from_uri(
            f"{dataset['Id']}/{version['version']}"
        )
        assert dataset_id == dataset["Id"]
        assert _version == version["version"]
        assert _edition == edition["edition"]

    def test_dataset_components_from_uri_full(self, mocker):
        cmd = create_cmd(mocker, "ls")
        dataset_id, _version, _edition = cmd._dataset_components_from_uri(
            f"{dataset['Id']}/{version['version']}/{edition['edition']}"
        )
        assert dataset_id == dataset["Id"]
        assert _version == version["version"]
        assert _edition == edition["edition"]

    def test_dataset_components_from_uri_latest_edition(self, mocker):
        cmd = create_cmd(mocker, "ls")
        dataset_id, _version, _edition = cmd._dataset_components_from_uri(
            f"{dataset['Id']}/{version['version']}/latest"
        )
        assert dataset_id == dataset["Id"]
        assert _version == version["version"]
        assert _edition == edition["edition"]

    def test_dataset_components_from_uri_create_edition(self, mocker):
        cmd = create_cmd(mocker, "ls")
        dataset_id, _version, _edition = cmd._dataset_components_from_uri(
            dataset["Id"], True
        )
        assert dataset_id == dataset["Id"]
        assert _version == version["version"]
        assert _edition == "new-edition"

    def test_dataset_components_from_uri_create_edition_with_version(self, mocker):
        cmd = create_cmd(mocker, "ls")
        dataset_id, _version, _edition = cmd._dataset_components_from_uri(
            f"{dataset['Id']}/{version['version']}", True
        )
        assert dataset_id == dataset["Id"]
        assert _version == version["version"]
        assert _edition == "new-edition"
