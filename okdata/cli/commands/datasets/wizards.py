from okdata.sdk.data.dataset import Dataset
from okdata.sdk.pipelines.client import PipelineApiClient
from questionary import prompt

from okdata.cli.commands.datasets.boilerplate.boilerplate import confidentiality_map
from okdata.cli.commands.datasets.boilerplate.config import boilerplate_questions


class DatasetCreateWizard:
    """Wizard for the `datasets create` command.

    Creates a new dataset with an optional pipeline based on the answers from a
    questionnaire.
    """

    def __init__(self, command):
        self.command = command

    def dataset_config(self, choices):
        title = choices["title"]
        access_rights = choices["accessRights"]

        return {
            "title": title,
            "description": choices["description"] or title,
            "keywords": choices["keywords"].split(","),
            "accessRights": access_rights,
            "confidentiality": confidentiality_map[access_rights],
            "objective": choices["objective"] or title,
            "contactPoint": {
                "name": choices["name"],
                "email": choices["email"],
                "phone": choices["phone"],
            },
            "publisher": choices["publisher"],
        }

    def pipeline_config(self, pipeline_processor_id, dataset_id, version):
        return {
            "pipelineProcessorId": pipeline_processor_id,
            "id": dataset_id,
            "datasetUri": f"output/{dataset_id}/{version}",
        }

    def pipeline_input_config(self, pipeline_id, dataset_id, version):
        return {
            "pipelineInstanceId": pipeline_id,
            "datasetUri": f"input/{dataset_id}/{version}",
            "stage": "raw",
        }

    def start(self):
        env = self.command.opt("env")
        choices = prompt(boilerplate_questions)

        self.command.print("Creating dataset...")
        dataset_client = Dataset(env=env)
        dataset_config = self.dataset_config(choices)
        dataset = dataset_client.create_dataset(dataset_config)
        dataset_id = dataset["Id"]
        self.command.print(f"Created dataset with ID: {dataset_id}")

        if choices["pipeline"]:
            self.command.print("Creating pipeline...")
            pipeline_client = PipelineApiClient(env=env)
            pipeline_config = self.pipeline_config(choices["pipeline"], dataset_id, "1")
            pipeline_id = pipeline_client.create_pipeline_instance(pipeline_config)
            pipeline_id = pipeline_id.strip('"')  # What's up with these?
            self.command.print(f"Created pipeline with ID: {pipeline_id}")

            self.command.print("Creating pipeline input...")
            pipeline_input_config = self.pipeline_input_config(
                pipeline_id, dataset_id, "1"
            )
            pipeline_input_id = pipeline_client.create_pipeline_input(
                pipeline_input_config
            )
            pipeline_input_id = pipeline_input_id.strip('"')  # What's up with these?
            self.command.print(f"Created pipeline input with ID: {pipeline_input_id}")

        self.command.print(
            f"""Done! You may go ahead and upload data to the dataset by running:

  okdata datasets cp FILE ds:{dataset_id}
"""
        )
