import json

from okdata.sdk.pipelines.client import PipelineApiClient

from okdata.cli.command import BaseCommand
from okdata.cli.commands.pipelines.inputs import PipelinesInputs
from okdata.cli.commands.pipelines.instances import (
    PipelineInstances,
    PipelinesLsInstances,
)
from okdata.cli.commands.pipelines.schemas import Schemas
from okdata.cli.output import create_output


class PipelinesLs(BaseCommand):
    """okdata::pipelines::ls
    usage:
      okdata pipelines ls [options]

    options:
      -d --debug
      --format=<format>
    """

    def handler(self):
        out = create_output(self.opt("format"), "pipelines_config.json")
        pipelines = self.sdk.get_pipelines()
        out.add_rows(pipelines)
        self.print("Available pipelines", out)


class PipelinesCreate(BaseCommand):
    """
    usage:
      okdata pipelines create - [options]
      okdata pipelines create <file> [options]

    options:
      -d --debug
      --format=<format>
    """

    def handler(self):
        content = self.handle_input()
        obj = json.loads(content)
        self.sdk.create_pipeline(obj)
        self.print(f"Created Pipeline with arn: {obj['arn']}", obj)


class Pipelines(BaseCommand):
    """
    usage:
      okdata pipelines --pipeline-arn=<pipeline-arn> [options]
      okdata pipelines instances ls [(<dataset-id> <version>)] [options]
      okdata pipelines instances create (<file> | -) [options]
      okdata pipelines ls [options]
      okdata pipelines ls-instances --pipeline-arn=<pipeline-arn> [options]
      okdata pipelines create (<file> | -) [options]
      okdata pipelines schemas [--id=<id>] [options]
      okdata pipelines schemas ls [options]
      okdata pipelines schemas create (<file> | -) [options]
      okdata pipelines inputs ls <pipeline-instance> [options]
      okdata pipelines inputs create (<file> | -) [options]

    options:
      -d --debug
      --format=<format>
    """

    def __init__(self):
        super().__init__(PipelineApiClient)
        self.sdk.login()
        self.sub_commands = [
            PipelinesLs,
            PipelinesCreate,
            PipelinesInputs,
            PipelineInstances,
            PipelinesLsInstances,
            Schemas,
        ]

    def handler(self):
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
