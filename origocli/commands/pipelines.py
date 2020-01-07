import json
from typing import Type

from origo.pipelines.client import PipelineApiClient
from origo.pipelines.resources.pipeline import Pipeline
from origo.pipelines.resources.pipeline_base import PipelineBase
from origo.pipelines.resources.pipeline_instance import PipelineInstance

from origocli.command import BaseCommand
from origocli.output import table_config_from_schema, TableOutput


class PipelineOutput:
    excluded = [
        "The Template Schema",
        "The Transformation_schema Schema",
    ]
    type = Pipeline
    config = table_config_from_schema(type, excluded)

class PipelineIntanceOutput:
    excluded = [
        "The Transformation Schema",
    ]
    type = PipelineInstance
    config = table_config_from_schema(type, excluded)


class Ls(BaseCommand):
    sdk: PipelineApiClient
    type: Type[PipelineBase]
    config: TableOutput

    def __init__(self, sdk):
        super().__init__()
        self.sdk = sdk
        self.handler = self.default

    def default(self):
        self.log.info(f"{self.type} ls")
        data = self.sdk.list(self.type)
        self.print_success(self.config, data)


class PipelinesLsInstances(Ls, PipelineIntanceOutput):
    """
    usage: origo pipelines ls-instances --pipeline-arn=<pipeline-arn> [options]

    options:
      -d --debug

    """
    sdk: PipelineApiClient

    def default(self):
        arn = self.args.get("--pipeline-arn")
        instances, error = self.sdk.get_pipeline(arn).list_instances()
        if error:
            raise error
        ddicts = list(map(lambda x: x.__dict__, instances))
        self.print_success(self.config, ddicts)


class PipelinesLs(Ls, PipelineOutput):
    """origo::pipelines::ls
    usage:
      origo pipelines ls [options]

    options:
      -d --debug
    """

class Create(BaseCommand):
    sdk: PipelineApiClient
    type: Type[PipelineBase]

    def __init__(self, sdk):
        super().__init__()
        self.sdk = sdk
        self.handler = self.default

    def default(self):
        content = self.handle_input()
        resource, error = self.type.from_json(self.sdk, content).create()
        if error:
            self.log.exception(error)
        self.pretty_json(resource)


class PipelinesCreate(Create, PipelineOutput):
    """
    usage:
      origo pipelines create - [options]
      origo pipelines create <file> [options]

    options:
      -d --debug
    """


class Pipelines(BaseCommand):
    """
    usage:
      origo pipelines --pipeline-arn=<pipeline-arn> [options]
      origo pipelines instances ls [(<dataset-id> <version>)] [options]
      origo pipelines instances create (<file> | -)
      origo pipelines ls [options]
      origo pipelines ls-instances --pipeline-arn=<pipeline-arn> [options]
      origo pipelines create (<file> | -)

    options:
      -d --debug
    """

    def __init__(self):
        super().__init__()
        self.sdk = PipelineApiClient()
        self.sdk.login()
        self.handler = self.default
        self.sub_commands = [
            PipelinesLs,
            PipelinesCreate,
            PipelineInstances,
            PipelinesLsInstances
        ]

    def default(self):
        pipeline = self.sdk.get_pipeline(self.args.get("--pipeline-arn"))
        output_dict = {
            "arn": pipeline.arn,
            "template": pipeline.template,
            "transformation_schema": json.loads(pipeline.transformation_schema),
        }
        self.pretty_json(output_dict)



class PipelineInstancesCreate(Create, PipelineIntanceOutput):
    """
    usage:
      origo pipelines instances create - [options]
      origo pipelines instances create <file> [options]

    options:
      -d --debug
    """


class PipelineInstanceLs(Ls, PipelineIntanceOutput):
    """usage:
      origo pipelines instances ls [(<dataset-id> <version>)] [options]

    options:
      -d --debug
    """
    def default(self):
        self.log.info(f"{self.type} ls")
        dataset_id = self.arg("dataset-id")
        version = self.arg("version")
        data = self.sdk.list(self.type)
        if dataset_id and version:
            data = filter(lambda instance: instance["datasetUri"] == f"output/{dataset_id}/{version}", data)
        self.print_success(self.config, data)


class PipelineInstances(BaseCommand, PipelineIntanceOutput):
    """
    usage:
      origo pipelines instances ls [(<dataset-id> <version>)] [options]
      origo pipelines instances create - [options]
      origo pipelines instances create <file> [options]

    options:
      -d --debug

    """
    sdk: PipelineApiClient

    def __init__(self, sdk):
        super().__init__()
        self.sdk = sdk
        self.handler = self.default
        self.sub_commands = [
            PipelineInstancesCreate,
            PipelineInstanceLs,
        ]

    def default(self):
        dataset_id = self.arg("dataset-id")
        version = self.arg("version")
        if dataset_id and version:
            result = next(filter(lambda instance: instance["datasetUri"] == f"output/{dataset_id}/{version}",
                                 self.sdk.get_pipeline_instances()))
            self.pretty_json(result)
        else:
            result = self.sdk.get_pipeline_instances()
            self.print_success(self.config, result)