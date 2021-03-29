import json
import inquirer
from inquirer.errors import ValidationError

from okdata.sdk.data.dataset import Dataset
from okdata.sdk.pipelines.resources.pipeline_instance import PipelineInstance

from okdata.cli.commands.pipelines.base import BasePipelinesCommand
from okdata.cli.output import create_output


class PipelinesLsInstances(BasePipelinesCommand):
    """
    usage: okdata pipelines ls-instances --pipeline-arn=<pipeline-arn> [options]

    options:
      -d --debug

    """

    def default(self):
        out = create_output(self.opt("format"), "pipelines_instances_config.json")
        arn = self.opt("pipeline-arn")
        instances, error = self.sdk.get_pipeline(arn).list_instances()
        if error:
            self.log.exception(error)
            return
        data = list(map(lambda x: x.__dict__, instances))
        out.add_rows(data)
        self.print(f"Instances with arn: {arn}", out)


class PipelineInstanceLs(BasePipelinesCommand):
    """usage:
      okdata pipelines instances ls [(<dataset-id> <version>)] [options]

    options:
      -d --debug
      --format=<format>
    """

    def default(self):
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


class PipelineInstancesCreate(BasePipelinesCommand):
    """
    usage:
      okdata pipelines instances create - [options]
      okdata pipelines instances create <file> [options]

    options:
      -d --debug
      --format=<format>
    """

    def default(self):
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


class PipelineInstances(BasePipelinesCommand):
    """
    usage:
      okdata pipelines instances ls [(<dataset-id> <version>)] [options]
      okdata pipelines instances wizard
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
            PipelineInstanceWizard,
        ]

    def default(self):
        self.help()


class PipelineInstanceWizard(BasePipelinesCommand):
    """usage:
      okdata pipelines instances wizard [options]

    options:
      -d --debug
    """

    def default(self):
        self.log.warning("==EXPERIMENTAL FEATURE==")
        ds_client = Dataset(config=self.sdk.config, auth=self.sdk.auth)
        datasets = ds_client.get_datasets()
        datasets = [dataset["Id"] for dataset in datasets]

        def validate_dataset(answers, current):
            if current not in datasets:
                raise ValidationError(False, reason="Dataset does not exist.")
            return True

        pipelines = self.sdk.get_pipelines()
        arns = [pipeline["arn"] for pipeline in pipelines]
        questions_1 = [
            inquirer.List("pipeline", message="Select a pipeline", choices=arns),
            inquirer.Text(
                "dataset-id",
                message="What is the output dataset ID ?",
                validate=validate_dataset,
            ),
        ]

        answers = inquirer.prompt(questions_1)
        versions = [
            version["version"]
            for version in ds_client.get_versions(answers["dataset-id"])
        ]

        questions_2 = [
            inquirer.List("version", message="Select a version", choices=versions),
        ]

        answers.update(inquirer.prompt(questions_2))

        pipeline_instance, error = PipelineInstance(
            self.sdk,
            id=answers["dataset-id"],
            pipelineArn=answers["pipeline"],
            datasetUri=f"output/{answers['dataset-id']}/{answers['version']}",
            taskConfig={},
        ).create()

        if error:
            self.log.exception(error)
            self.log.exception(error.response.text)
            return
        self.print("Success!")
        self.pretty_json(pipeline_instance)
