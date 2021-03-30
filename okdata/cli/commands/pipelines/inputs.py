import json

from okdata.cli.commands.pipelines.base import BasePipelinesCommand
from okdata.cli.output import create_output


class PipelinesInputsLs(BasePipelinesCommand):
    """
    usage:
      okdata pipelines inputs ls <pipeline-instance> [options]

    options:
      -d --debug
      --format=<format>
    """

    def default(self):
        out = create_output(
            self.opt("format"), "pipelines_instances_inputs_config.json"
        )
        data = self.sdk.get_pipeline_inputs(self.arg("pipeline-instance"))
        data = list(map(lambda x: x.__dict__, data))
        out.add_rows(data)
        self.print("Available pipepline inputs", out)


class PipelinesInputsCreate(BasePipelinesCommand):
    """
    usage:
      okdata pipelines inputs create - [options]
      okdata pipelines inputs create <file> [options]

    options:
      -d --debug
      --format=<format>
    """

    def default(self):
        content = self.handle_input()
        data = json.loads(content)
        self.sdk.create_pipeline_input(data)
        self.print(f"Created input with dataset URI: {data['datasetUri']}", data)


class PipelinesInputs(BasePipelinesCommand):
    """
    usage:
      okdata pipelines inputs ls <pipeline-instance> [options]
      okdata pipelines inputs create (<file> | -) [options]

    options:
      -d --debug
      --format=<format>
    """

    def __init__(self, sdk):
        super().__init__(sdk)
        self.sub_commands = [PipelinesInputsLs, PipelinesInputsCreate]

    def default(self):
        if self.opt("help"):
            return self.help()
        schema = self.sdk.get_schema(self.opt("id"))
        schema.schema = json.loads(schema.schema)
        self.pretty_json(schema.__dict__)
        return None
