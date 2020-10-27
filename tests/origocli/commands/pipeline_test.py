import logging

import requests
from origo.pipelines.client import PipelineApiClient
from origo.pipelines.resources.pipeline import Pipeline
from origo.pipelines.resources.pipeline_instance import PipelineInstance
from origo.sdk import SDK

from conftest import set_argv, BASECMD_QUAL
from origocli.commands.pipelines.pipelines import (
    Pipelines,
    PipelinesCreate,
    PipelinesLs,
)
from origocli.commands.pipelines.instances import (
    PipelinesLsInstances,
    PipelineInstanceLs,
)
from origocli.commands.pipelines.schemas import SchemasLs, SchemasCreate

pipeline_qual = f"{Pipeline.__module__}.{Pipeline.__name__}"
pipeline_client_qual = f"{PipelineApiClient.__module__}.{PipelineApiClient.__name__}"

sdk = PipelineApiClient()


def _HTTPError400():
    response = requests.Response()
    response.status_code = 400
    return requests.HTTPError("400 Client Error", response=response)


class TestPipelines:
    def test_handler(self, mocker, capsys):
        set_argv(
            "pipelines",
            "--pipeline-arn",
            "arn:aws:states:eu-west-1:123456789102:stateMachine:mocked",
            "--format=json",
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
        assert (
            captured.out.strip()
            == '{"arn": "arn:aws:states:eu-west-1:123456789102:stateMachine:mocked", "template": "", "transformation_schema": {}}'
        )


class TestCreate:
    def test_handler(self, mocker, capsys):
        set_argv("pipelines", "create", "something.json", "--format=json")
        mocker.patch(
            "builtins.open",
            mocker.mock_open(
                read_data='{"arn": "arn", "template": "", "transformation_schema": ""}'
            ),
        )
        mocker.patch(
            f"{pipeline_qual}.from_json", return_value=Pipeline(sdk, "", "", "")
        )
        create = mocker.patch(
            f"{pipeline_qual}.create", return_value=['"pipeline-arn"', None]
        )
        cmd = PipelinesCreate(sdk)
        cmd.handler()
        captured = capsys.readouterr()
        assert create.called
        assert (
            captured.out.strip()
            == '{"arn": "arn", "template": "", "transformation_schema": ""}'
        )

    def test_handler_with_create_error(self, mocker):
        set_argv("pipelines", "create", "something.json", "--format=json")

        sdk = PipelineApiClient()
        mocker.patch(
            "builtins.open",
            mocker.mock_open(
                read_data='{"arn": "arn", "template": "", "transformation_schema": ""}'
            ),
        )
        mocker.patch(
            f"{pipeline_qual}.from_json", return_value=Pipeline(sdk, "", "", "")
        )
        mocker.patch(
            f"{pipeline_qual}.create",
            return_value=[None, _HTTPError400()],
        )
        cmd = PipelinesCreate(sdk)
        try:
            cmd.handler()
            assert False
        except Exception:
            assert True


class TestPipelinesLs:
    def test_handler(self, mocker):
        set_argv("pipelines", "ls")
        list = mocker.patch(f"{pipeline_client_qual}.list")
        print = mocker.patch(f"{BASECMD_QUAL}.print")
        PipelinesLs(PipelineApiClient()).handler()
        assert list.called
        assert print.called


class TestPipelinesLsInstances:
    def test_handler(self, mocker):
        set_argv("pipelines", "ls-instances", "--pipeline-arn", "pipeline-arn")
        print_result = mocker.patch(f"{BASECMD_QUAL}.print")
        pipeline = mocker.patch(
            f"{pipeline_client_qual}.get_pipeline",
            return_value=Pipeline(sdk, "", "", ""),
        )
        instances = mocker.patch(
            f"{pipeline_qual}.list_instances",
            return_value=(
                [
                    PipelineInstance(sdk, "1", "", "", False),
                    PipelineInstance(sdk, "2", "", "", False),
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
        caplog.set_level(logging.ERROR)

        pipeline = mocker.patch(
            f"{pipeline_client_qual}.get_pipeline",
            return_value=Pipeline(sdk, "", "", ""),
        )
        instances = mocker.patch(
            f"{pipeline_qual}.list_instances",
            return_value=([], _HTTPError400()),
        )
        cmd = PipelinesLsInstances(sdk)

        cmd.handler()

        assert pipeline.called
        assert instances.called
        assert any(
            record.message.startswith("400 Client Error") for record in caplog.records
        )


class TestPipelineInstanceLs:
    def test_handler_all(self, mocker, mock_print_success, capsys):
        set_argv("pipelines", "instances", "ls", "--format=json")
        cmd = PipelineInstanceLs(sdk)
        list = mocker.patch(
            f"{pipeline_client_qual}.list",
            return_value=[
                PipelineInstance(
                    sdk, "1", "output/dataset-id/version-1", "", False
                ).__dict__,
                PipelineInstance(
                    sdk, "2", "output/dataset-id/version-2", "", False
                ).__dict__,
            ],
        )

        cmd.handler()
        captured = capsys.readouterr()
        assert list.called
        assert (
            captured.out.strip()
            == '[{"id": "1", "datasetUri": "output/dataset-id/version-1", "pipelineArn": "N/A"}, {"id": "2", "datasetUri": "output/dataset-id/version-2", "pipelineArn": "N/A"}]'
        )

    def test_handler_dataset_version(self, mocker, mock_pretty_json, capsys):
        set_argv(
            "pipelines", "instances", "ls", "dataset-id", "version-2", "--format=json"
        )
        cmd = PipelineInstanceLs(sdk)
        list = mocker.patch(
            f"{pipeline_client_qual}.list",
            return_value=[
                PipelineInstance(
                    sdk, "1", "output/dataset-id/version-1", "", False
                ).__dict__,
                PipelineInstance(
                    sdk, "2", "output/dataset-id/version-2", "", False
                ).__dict__,
            ],
        )
        cmd.handler()
        captured = capsys.readouterr()
        assert list.called
        assert (
            captured.out.strip()
            == '[{"id": "2", "datasetUri": "output/dataset-id/version-2", "pipelineArn": "N/A"}]'
        )


class TestSchemas:
    def test_handler_ls(self, mocker, mock_print_success):
        set_argv("pipelines", "schemas", "ls")
        cmd = SchemasLs(sdk)
        assert cmd

    def test_handler_create(self, mocker, mock_print_success):
        set_argv("pipelines", "schemas", "create", "test.json")
        cmd = SchemasCreate(sdk)
        assert cmd
