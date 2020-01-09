import json
import sys
from typing import Type

import inquirer
from inquirer.errors import ValidationError
from origo.data.dataset import Dataset
from origo.pipelines.client import PipelineApiClient
from origo.pipelines.resources.pipeline import Pipeline
from origo.pipelines.resources.pipeline_base import PipelineBase
from origo.pipelines.resources.pipeline_instance import PipelineInstance

from origocli.command import BaseCommand
from origocli.output import table_config_from_schema, TableOutput
from fuzzywuzzy import process


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
      origo pipelines instances wizard
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
            PipelinesLsInstances,
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
            data = filter(
                lambda instance: instance["datasetUri"]
                == f"output/{dataset_id}/{version}",
                data,
            )
        self.print_success(self.config, data)


class PipelineInstances(BaseCommand, PipelineIntanceOutput):
    """
    usage:
      origo pipelines instances ls [(<dataset-id> <version>)] [options]
      origo pipelines instances wizard
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
            PipelineInstanceWizard,
        ]

    def default(self):
        dataset_id = self.arg("dataset-id")
        version = self.arg("version")
        if dataset_id and version:
            result = next(
                filter(
                    lambda instance: instance["datasetUri"]
                    == f"output/{dataset_id}/{version}",
                    self.sdk.get_pipeline_instances(),
                )
            )
            self.pretty_json(result)
        else:
            result = self.sdk.get_pipeline_instances()
            self.print_success(self.config, result)


class PipelineInstanceWizard(BaseCommand, PipelineIntanceOutput):
    """usage:
      origo pipelines instances wizard [options]

    options:
      -d --debug
    """

    sdk: PipelineApiClient

    def __init__(self, sdk):
        super().__init__()
        self.sdk = sdk
        self.handler = self.default

    def default(self):
        ds_client = Dataset(config=self.sdk.config, auth=self.sdk.auth)
        datasets = ds_client.get_datasets()
        datasets = [dataset["Id"] for dataset in datasets]

        def validate_dataset(answers, current):
            if current not in datasets:
                possible_matches = process.extractBests(current, datasets, limit=3)
                possible_matches = [match[0] for match in possible_matches]
                raise ValidationError(
                    False,
                    reason=f"Dataset does not exist. Similar datasets ids include: {possible_matches}",
                )
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
            inquirer.Editor(
                "transformation", message="Provide a transformation object"
            ),
            inquirer.Text(
                "schema-id",
                message="Use a schema? Please enter schema-id (empty for no schema)",
                default="",
            ),
            inquirer.List(
                "create-edition",
                message="Should a new edition be created after this pipeline succeeds? (default: True)",
                choices=[True, False],
            ),
        ]

        answers.update(inquirer.prompt(questions_2))

        pipeline_instance, error = PipelineInstance(
            self.sdk,
            id=answers["dataset-id"],
            pipelineArn=answers["pipeline"],
            datasetUri=f"output/{answers['dataset-id']}/{answers['version']}",
            schemaId=answers["schema-id"],
            transformation=json.loads(answers["transformation"]),
            useLatestEdition=not answers["create-edition"],
        ).create()

        if error:
            self.log.exception(error)
            self.log.exception(error.response.text)
            sys.exit(1)
        self.print("Success!")
        self.pretty_json(pipeline_instance)
