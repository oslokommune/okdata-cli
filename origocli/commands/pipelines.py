import json
import logging
from origo.pipelines.client import PipelineApiClient
from origo.pipelines.resources.pipeline import Pipeline
from origo.pipelines.resources.pipeline_instance import PipelineInstance

from origocli.commands.common import BaseCommand

class PipelinesLsInstances(BaseCommand):
    """
    usage: origo pipelines ls instances --pipeline-arn=<pipeline-arn> [options]

    options:
      -d --debug

    """
    sdk: PipelineApiClient

    def __init__(self, sdk):
        self.sdk = sdk
        self.handler = self.default

    def default(self):
        logging.basicConfig(level=logging.DEBUG)
        arn = self.args.get("--pipeline-arn")
        instances, error = self.sdk.get_pipeline(arn).list_instances()
        if error:
            raise error
        ddicts = list(map(lambda x: x.__dict__, instances))
        self.print_success(PipelineInstance, ddicts)


class PipelineInstanceCreateCommand(BaseCommand):
    """
    usage:
      origo pipelines instances create - [options]
      origo pipelines instances create <file> [options]

    options:
      -d --debug
    """
    sdk : PipelineApiClient
    def __init__(self, sdk):
        self.sdk = sdk
        self.handler = self.default

    def default(self):
        content = self.handle_input()
        instance = self.sdk.create_pipeline_instance(content)
        self.pretty_json(instance)

class PipelineInstances(BaseCommand):
    """
    usage:
      origo pipelines instances [(<dataset-id> <version>)]
      origo pipelines instances create - [options]
      origo pipelines instances create <file> [options]

    options:
      -d --debug

    """
    sdk: PipelineApiClient

    def __init__(self, sdk):
        self.sdk = sdk
        self.handler = self.default
        self.sub_commands = {
            "create": PipelineInstanceCreateCommand
        }

    def default(self):
        dataset_id = self.arg("dataset-id")
        version = self.arg("version")
        if dataset_id and version:
            result = next(filter(lambda instance: instance["datasetUri"] == f"output/{dataset_id}/{version}", self.sdk.get_pipeline_instances()))
            self.pretty_json(result)
        else:
            result = self.sdk.get_pipeline_instances()
            self.print_success(PipelineInstance, result)



class PipelinesLsCommand(BaseCommand):
    """origo::pipelines::ls
    usage:
      origo pipelines ls [options]
      origo pipelines ls instances --pipeline-arn=<pipeline-arn> [options]

    options:
      -d --debug
    """
    sdk: PipelineApiClient

    def __init__(self, sdk):
        self.sdk = sdk
        self.handler = self.default
        self.sub_commands = {
            "instances": PipelinesLsInstances
        }

    def default(self):
        self.log.info("Pipelines ls")
        data = self.sdk.get_pipelines()
        self.print_success(Pipeline, data)

class PipelinesCreateCommand(BaseCommand):
    """
    usage:
      origo pipelines create - [options]
      origo pipelines create <file> [options]

    options:
      -d --debug
    """
    sdk : PipelineApiClient
    def __init__(self, sdk):
        self.sdk = sdk
        self.handler = self.default

    def default(self):
        content = self.handle_input()
        pipeline = self.sdk.create_pipeline(content)
        self.pretty_json(pipeline)

class PipelinesCommand(BaseCommand):
    """
    usage:
      origo pipelines [options]
      origo pipelines instances [(<dataset-id> <version>)] [options]
      origo pipelines instances create (<file> | -)
      origo pipelines ls [options]
      origo pipelines ls instances [options]
      origo pipelines create (<file> | -)

    options:
      -d --debug
      --pipeline-arn=<pipeline-arn>
    """

    def __init__(self):
        self.sdk = PipelineApiClient()
        self.sdk.login()
        self.handler = self.default
        self.sub_commands = {
            "ls": PipelinesLsCommand,
            "create": PipelinesCreateCommand,
            "instances": PipelineInstances
        }

    def default(self):
        pipeline = self.sdk.get_pipeline(self.args.get("--pipeline-arn"))
        output_dict = {
            "arn": pipeline.arn,
            "template": pipeline.template,
            "transformation_schema": json.loads(pipeline.transformation_schema),
        }
        self.pretty_json(output_dict)
