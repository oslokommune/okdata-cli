import json
from json import JSONDecodeError

import inquirer
import jsonschema
from fuzzywuzzy import process
from inquirer.errors import ValidationError
from jsonschema import ValidationError as SchemaValidationError
from origo.data.dataset import Dataset
from origo.pipelines.client import PipelineApiClient
from origo.pipelines.resources.pipeline_instance import PipelineInstance
from requests import HTTPError

from origocli.command import BaseCommand


class MissingVersionExit(SystemExit):
    def __init__(self):
        super().__init__("missing Version in dataset metadata")


class InvalidTransformation(Exception):
    def __init__(self, errors):
        super().__init__("invalid transformation schema: ", errors)


def select_dataset(sdk: Dataset, datasets=None):
    if datasets is None:
        datasets = sdk.get_datasets()
    dataset_ids = [dataset["Id"] for dataset in datasets]

    def validate_dataset(answers, current):
        if current not in dataset_ids:
            possible_matches = process.extractBests(current, dataset_ids, limit=5)
            possible_matches = [match[0] for match in possible_matches]
            reason = f"Dataset does not exist. Similar datasets ids include: {' '.join(possible_matches)}"
            raise ValidationError(
                    False,
                    reason=reason,
            )
        return True

    q = [inquirer.Text(
            "dataset-id",
            message="What is the output dataset ID ?",
            validate=validate_dataset,
    )]
    answers = inquirer.prompt(q)
    return next(dataset for dataset in datasets if answers["dataset-id"] == dataset["Id"])


def select_pipeline(sdk: PipelineApiClient, pipelines=None):
    if pipelines is None:
        pipelines = sdk.get_pipelines()
    arns = [pipeline["arn"] for pipeline in pipelines]

    q = [inquirer.List("pipeline", message="Select a pipeline", choices=arns)]
    answers = inquirer.prompt(q)
    return next(pipeline for pipeline in pipelines if answers["pipeline"] == pipeline["arn"])


def select_version(sdk: Dataset, dataset_id):
    versions = sdk.get_versions(dataset_id)
    if len(versions) < 1:
        raise MissingVersionExit
    all_versions = [version["version"] for version in versions]

    q = [inquirer.List("version", message="Select a version", choices=all_versions)]
    answers = inquirer.prompt(q)
    return next(version for version in versions if answers["version"] == version["version"])


def pipeline_instance_wizard(sdk: Dataset, dataset: dict = None, pipeline=None):
    if dataset is None:
        dataset = select_dataset(sdk)
    version = select_version(sdk, dataset["Id"])
    if pipeline is None:
        pipeline = select_pipeline(PipelineApiClient(config=sdk.config, auth=sdk.auth))

    try:
        transformation_schema = json.loads(pipeline["transformation_schema"])
        example = json.dumps(json_schema_example(transformation_schema), indent=2)
        example = example.replace("{", "{{")
        example = example.replace("}", "}}")
    except Exception:
        example = ""
        transformation_schema = None

    transformation_q = inquirer.Text("transformation", message="Provide a transformation object", default=example)
    transformation_q.kind = "editor"

    questions = [
        inquirer.Text(
                "schema-id",
                message="Use a schema? Please enter schema-id (empty for no schema)",
                default="",
        ),
        inquirer.List(
                "create-edition",
                message="Should a new edition be created after this pipeline succeeds?",
                choices=[True, False],
        ),
        transformation_q
    ]

    answers = inquirer.prompt(questions)

    while transformation_schema is not None:
        try:
            jsonschema.validate(json.loads(answers["transformation"]),
                                schema=transformation_schema)
        except SchemaValidationError as e:
            print("Input must match the transformation Schema: ")
            BaseCommand.pretty_json(e.schema)
            print(e.__repr__())
            answers.update(
                inquirer.prompt([transformation_q]))
        except JSONDecodeError:
            print("Not valid JSON!")
            answers.update(
                    inquirer.prompt([transformation_q]))
        else:
            break

    pipeline_instance = PipelineInstance(
            sdk,
            id=dataset['Id'],
            pipelineArn=pipeline["arn"],
            datasetUri=f"output/{dataset['Id']}/{version['version']}",
            schemaId=answers["schema-id"],
            transformation=json.loads(answers["transformation"]),
            useLatestEdition=not answers["create-edition"],
    )
    response, error = pipeline_instance.create()

    if error:
        raise SystemExit(error, error.response.text)

    return pipeline_instance


def zero_init(type):
    if type == "string":
        return ""
    elif type == "integer" or type == "number":
        return 0
    elif type == "boolean":
        return False
    elif type == "null":
        return None
    else:
        raise Exception("illegal Json schema type: ", type)


def json_schema_example(schema):
    example = {}
    for name, prop in schema["properties"].items():
        if prop["type"] == "object":
            example[name] = json_schema_example(prop)
        else:
            example[name] = zero_init(prop["type"])
    return example
