import json

from okdata.sdk.pipelines.resources.pipeline_instance import PipelineInstance

from okdata.cli.command import BaseCommand
from okdata.cli.output import create_output


class PipelinesLsInstances(BaseCommand):
    """
    usage: okdata pipelines ls-instances --pipeline-arn=<pipeline-arn> [options]

    options:
      -d --debug

    """

    def handler(self):
        out = create_output(self.opt("format"), "pipelines_instances_config.json")
        arn = self.opt("pipeline-arn")
        instances, error = self.sdk.get_pipeline(arn).list_instances()
        if error:
            self.log.exception(error)
            return
        data = list(map(lambda x: x.__dict__, instances))
        out.add_rows(data)
        self.print(f"Instances with arn: {arn}", out)


class PipelineInstanceLs(BaseCommand):
    """usage:
      okdata pipelines instances ls [(<dataset-id> <version>)] [options]

    options:
      -d --debug
      --format=<format>
    """

    def handler(self):
        out = create_output(self.opt("format"), "pipelines_instances_config.json")
        dataset_id = self.arg("dataset-id")
        version = self.arg("version")
        data = self.sdk.list(PipelineInstance)
        title = ""
        if dataset_id and version:
            data = [
                instance
                for instance in data
                if instance["datasetUri"] == f"output/{dataset_id}/{version}"
            ]
            out.add_rows(data)
            title = "Pipeline instance"
        else:
            out.add_rows(data)
            title = "Pipeline instances"
        self.print(title, out)


class PipelineInstancesCreate(BaseCommand):
    """
    usage:
      okdata pipelines instances create - [options]
      okdata pipelines instances create <file> [options]

    options:
      -d --debug
      --format=<format>
    """

    def handler(self):
        out = create_output(self.opt("format"), "pipelines_instances_config.json")
        self.log.info("PipelineInstancesCreate")
        content = self.handle_input()
        resource, error = PipelineInstance.from_json(self.sdk, content).create()
        if error:
            self.print(f"ERROR: {error} from: {content}")
            self.log.exception(error)
            return
        originaldata = json.loads(content)
        data = {
            "id": json.loads(resource),
            "datasetUri": originaldata["datasetUri"],
        }
        if "pipelineProcessorId" in originaldata:
            data["pipelineProcessorId"] = originaldata["pipelineProcessorId"]
        out.output_singular_object = True
        out.add_row(data)
        self.print("Created resources", out)


class PipelineInstances(BaseCommand):
    """
    usage:
      okdata pipelines instances ls [(<dataset-id> <version>)] [options]
      okdata pipelines instances create - [options]
      okdata pipelines instances create <file> [options]

    options:
      -d --debug
      --format=<format>
    """

    def __init__(self, sdk):
        super().__init__(sdk)
        self.sub_commands = [
            PipelineInstancesCreate,
            PipelineInstanceLs,
        ]

    def handler(self):
        self.help()
