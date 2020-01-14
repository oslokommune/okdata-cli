import logging
from datetime import datetime

import pytest
from origo.data.dataset import Dataset

from conftest import set_argv
from origocli.commands.datasets import DatasetsCommand
from origocli.output import TableOutput

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

edition = {"edition": datetime.now().isoformat()}


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
    cmd.sdk.get_editions.return_value = [edition, edition2]
    cmd.sdk.get_edition.return_value = edition
    return cmd


class TestDatasetsLs:
    def test_datasets(self, mock_print, mocker, output):
        cmd = create_cmd(mocker, "ls")
        cmd.handler()
        assert output_with_argument(output, [dataset, dataset])
        assert mock_print.called_once

    def test_datasets_error(self, mocker, mock_print):
        cmd = create_cmd(mocker, "ls")
        cmd.sdk.get_datasets.side_effect = Exception("test")
        cmd.handler()
        logging.basicConfig(level=logging.DEBUG)

        cmd.log.exception.assert_called_once_with(f"Failed badly: test")
        assert not mock_print.called

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

    def test_dataset_error(self, mocker, mock_print):
        cmd = create_cmd(mocker, "ls", dataset["Id"])
        cmd.sdk.get_latest_version.side_effect = Exception("test")
        cmd.handler()
        assert cmd.sdk.get_dataset.called
        assert cmd.sdk.get_versions.called
        assert cmd.sdk.get_latest_version.called
        assert cmd.log.exception.called
        assert not mock_print.called

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
