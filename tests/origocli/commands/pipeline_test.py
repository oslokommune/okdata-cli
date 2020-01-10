import json
import logging

import requests
from origo.pipelines.client import PipelineApiClient
from origo.pipelines.resources.pipeline import Pipeline
from origo.pipelines.resources.pipeline_instance import PipelineInstance
from origo.sdk import SDK
from requests import HTTPError

from conftest import set_argv, BASECMD_QUAL
from origocli.command import BaseCommand
from origocli.commands.pipelines import (
    Pipelines,
    PipelinesCreate,
    PipelinesLs,
    PipelinesLsInstances,
    PipelineInstanceLs,
    PipelineInstances,
)

pipeline_qual = f"{Pipeline.__module__}.{Pipeline.__name__}"
pipeline_client_qual = f"{PipelineApiClient.__module__}.{PipelineApiClient.__name__}"


class TestPipelines:
    def test_handler(self, mocker, capsys):
        set_argv(
            "pipelines",
            "--pipeline-arn",
            "arn:aws:states:eu-west-1:123456789102:stateMachine:mocked",
        )
        pipeline = Pipeline(
            SDK(),
            "arn:aws:states:eu-west-1:123456789102:stateMachine:mocked",
            template="",
            transformation_schema="{}",
        )
        mocker.patch(f"{pipeline_client_qual}.get_pipeline", return_value=pipeline)

        cmd = Pipelines()

        cmd.handler()
        captured = capsys.readouterr()
        prepare_expected = pipeline.__dict__
        prepare_expected["transformation_schema"] = json.loads(
            prepare_expected["transformation_schema"]
        )
        BaseCommand.pretty_json(prepare_expected)
        expected = capsys.readouterr()
        assert captured.out == expected.out


class TestCreate:
    def test_handler(self, mocker, capsys):
        set_argv("pipelines", "create", "something.json")
        sdk = PipelineApiClient()
        mocker.patch("builtins.open", mocker.mock_open(read_data="open_file"))
        mocker.patch(
            f"{pipeline_qual}.from_json", return_value=Pipeline(sdk, "", "", "")
        )
        mocker.patch(f"{pipeline_qual}.create", return_value=['"pipeline-arn"', None])
        cmd = PipelinesCreate(sdk)
        cmd.handler()

    def test_handler_with_create_error(self, mocker, caplog):
        set_argv("pipelines", "create", "something.json")
        caplog.set_level(logging.ERROR)

        sdk = PipelineApiClient()
        try:
            requests.get("https://httpstat.us/400").raise_for_status()
        except HTTPError as he:
            he_400 = he
        mocker.patch("builtins.open", mocker.mock_open(read_data="open_file"))
        mocker.patch(
            f"{pipeline_qual}.from_json", return_value=Pipeline(sdk, "", "", "")
        )
        mocker.patch(f"{pipeline_qual}.create", return_value=[None, he_400])
        cmd = PipelinesCreate(sdk)
        cmd.handler()
        assert any(
            record.message.startswith("400 Client Error") for record in caplog.records
        )


class TestPipelinesLs:
    def test_handler(self, mocker):
        set_argv("pipelines", "ls")
        list = mocker.patch(f"{pipeline_client_qual}.list")
        print = mocker.patch(f"{BASECMD_QUAL}.print_success")
        PipelinesLs(PipelineApiClient()).handler()
        assert list.called
        assert print.called


class TestPipelinesLsInstances:
    def test_handler(self, mocker):
        set_argv("pipelines", "ls-instances", "--pipeline-arn", "pipeline-arn")
        sdk = PipelineApiClient()

        print_result = mocker.patch(f"{BASECMD_QUAL}.print_success")
        pipeline = mocker.patch(
            f"{pipeline_client_qual}.get_pipeline",
            return_value=Pipeline(sdk, "", "", ""),
        )
        instances = mocker.patch(
            f"{pipeline_qual}.list_instances",
            return_value=(
                [
                    PipelineInstance(sdk, "1", "", "", "", "", False),
                    PipelineInstance(sdk, "2", "", "", "", "", False),
                ],
                None,
            ),
        )
        cmd = PipelinesLsInstances(sdk)

        cmd.handler()

        assert pipeline.called
        assert instances.called
        assert print_result.called

    def test_handler_with_http_error(self, mocker, caplog):
        set_argv("pipelines", "ls-instances", "--pipeline-arn", "pipeline-arn")
        sdk = PipelineApiClient()
        caplog.set_level(logging.ERROR)
        try:
            requests.get("https://httpstat.us/400").raise_for_status()
        except HTTPError as he:
            he_400 = he

        pipeline = mocker.patch(
            f"{pipeline_client_qual}.get_pipeline",
            return_value=Pipeline(sdk, "", "", ""),
        )
        instances = mocker.patch(
            f"{pipeline_qual}.list_instances", return_value=([], he_400)
        )
        cmd = PipelinesLsInstances(sdk)

        cmd.handler()

        assert pipeline.called
        assert instances.called
        assert any(
            record.message.startswith("400 Client Error") for record in caplog.records
        )


class TestPipelineInstanceLs:
    def test_handler_all(self, mocker, mock_print_success):
        set_argv("pipelines", "instances", "ls")
        sdk = PipelineApiClient()
        list = mocker.patch(
            f"{pipeline_client_qual}.list",
            return_value=[
                PipelineInstance(sdk, "1", "", "", "", "", False).__dict__,
                PipelineInstance(sdk, "2", "", "", "", "", False).__dict__,
            ],
        )
        cmd = PipelineInstanceLs(sdk)
        cmd.handler()

        assert list.called
        assert mock_print_success.called

    def test_handler_with_ds_version(self, mocker, mock_print_success):
        set_argv("pipelines", "instances", "ls", "dataset-id", "version-1")
        sdk = PipelineApiClient()
        list = mocker.patch(
            f"{pipeline_client_qual}.list",
            return_value=[
                PipelineInstance(
                    sdk, "1", "output/dataset-id/version-1", "", "", "", False
                ).__dict__,
                PipelineInstance(
                    sdk, "2", "output/dataset-id/version-2", "", "", "", False
                ).__dict__,
            ],
        )
        cmd = PipelineInstanceLs(sdk)
        cmd.handler()

        assert list.called
        assert mock_print_success.called
        assert [
            PipelineInstance(
                sdk, "1", "output/dataset-id/version-1", "", "", "", False
            ).__dict__
        ] in mock_print_success.call_args[0]


class TestPipelineInstances:
    def test_handler_all(self, mocker, mock_print_success):
        set_argv("pipelines", "instances", "ls")
        sdk = PipelineApiClient()
        cmd = PipelineInstances(sdk)
        list = mocker.patch(
            f"{pipeline_client_qual}.list",
            return_value=[
                PipelineInstance(
                    sdk, "1", "output/dataset-id/version-1", "", "", "", False
                ).__dict__,
                PipelineInstance(
                    sdk, "2", "output/dataset-id/version-2", "", "", "", False
                ).__dict__,
            ],
        )

        cmd.handler()
        assert list.called
        assert len(mock_print_success.call_args[0][1]) == 2

    def test_handler_dataset_version(self, mocker, mock_pretty_json):
        set_argv("pipelines", "instances", "ls", "dataset-id", "version-2")
        sdk = PipelineApiClient()
        cmd = PipelineInstances(sdk)
        list = mocker.patch(
            f"{pipeline_client_qual}.list",
            return_value=[
                PipelineInstance(
                    sdk, "1", "output/dataset-id/version-1", "", "", "", False
                ).__dict__,
                PipelineInstance(
                    sdk, "2", "output/dataset-id/version-2", "", "", "", False
                ).__dict__,
            ],
        )
        cmd.handler()
        assert list.called
        assert (
            PipelineInstance(
                sdk, "2", "output/dataset-id/version-2", "", "", "", False
            ).__dict__
            in mock_pretty_json.call_args[0]
        )
