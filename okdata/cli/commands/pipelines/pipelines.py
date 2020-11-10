import json

from origo.pipelines.client import PipelineApiClient

from origocli.command import BaseCommand
from origocli.commands.pipelines.base import BasePipelinesCommand
from origocli.commands.pipelines.instances import (
    PipelineInstances,
    PipelinesLsInstances,
)
from origocli.commands.pipelines.schemas import Schemas
from origocli.commands.pipelines.inputs import PipelinesInputs
from origocli.output import create_output


class PipelinesLs(BasePipelinesCommand):
    """origo::pipelines::ls
    usage:
      origo pipelines ls [options]

    options:
      -d --debug
      --format=<format>
    """

    def default(self):
        out = create_output(self.opt("format"), "pipelines_config.json")
        pipelines = self.sdk.get_pipelines()
        out.add_rows(pipelines)
        self.print("Available pipelines", out)


class PipelinesCreate(BasePipelinesCommand):
    """
    usage:
      origo pipelines create - [options]
      origo pipelines create <file> [options]

    options:
      -d --debug
      --format=<format>
    """

    def default(self):
        content = self.handle_input()
        obj = json.loads(content)
        self.sdk.create_pipeline(obj)
        self.print(f"Created Pipeline with arn: {obj['arn']}", obj)


class Pipelines(BaseCommand):
    """
    usage:
      origo pipelines --pipeline-arn=<pipeline-arn> [options]
      origo pipelines instances ls [(<dataset-id> <version>)] [options]
      origo pipelines instances create (<file> | -) [options]
      origo pipelines instances wizard
      origo pipelines ls [options]
      origo pipelines ls-instances --pipeline-arn=<pipeline-arn> [options]
      origo pipelines create (<file> | -) [options]
      origo pipelines schemas [--id=<id>] [options]
      origo pipelines schemas ls [options]
      origo pipelines schemas create (<file> | -) [options]
      origo pipelines inputs ls <pipeline-instance> [options]
      origo pipelines inputs create (<file> | -) [options]

    options:
      -d --debug
      --format=<format>
    """

    def __init__(self):
        super().__init__()
        self.sdk = PipelineApiClient()
        self.sdk.login()
        self.handler = self.default
        self.sub_commands = [
            PipelinesLs,
            PipelinesCreate,
            PipelinesInputs,
            PipelineInstances,
            PipelinesLsInstances,
            Schemas,
        ]

    def default(self):
        arn = self.args.get("--pipeline-arn")
        pipeline = self.sdk.get_pipeline(arn)
        if self.opt("format") == "json":
            output_dict = {
                "arn": pipeline.arn,
                "template": pipeline.template,
                "transformation_schema": json.loads(pipeline.transformation_schema),
            }
            self.print("", output_dict)
            return
        self.print(f"Pipeline: {arn}")
        if not pipeline.template:
            self.print("No template registered")
        else:
            self.pretty_json(pipeline.template)
        if not pipeline.transformation_schema:
            self.print("No transfomration schema registered")
        else:
            self.print("Transformation schema")
            self.pretty_json(json.loads(pipeline.transformation_schema))
