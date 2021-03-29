import json

from okdata.cli.commands.pipelines.base import BasePipelinesCommand
from okdata.cli.output import create_output


class SchemasLs(BasePipelinesCommand):
    """okdata::pipelines::ls
    usage:
      okdata pipelines schemas ls [options]

    options:
      -d --debug
      --format=<format>
    """

    def default(self):
        out = create_output(
            self.opt("format"), "pipelines_instances_schemas_config.json"
        )
        schemas = self.sdk.get_schemas()
        out.add_rows(schemas)
        self.print("List of Schemas available", out)


class SchemasCreate(BasePipelinesCommand):
    """
    usage:
      okdata pipelines schemas create - [options]
      okdata pipelines schemas create <file> [options]

    options:
      -d --debug
      --format=<format>
    """

    def default(self):
        content = self.handle_input()
        obj = json.loads(content)
        data = {"id": obj["id"], "type": "schema", "schema": json.dumps(obj["schema"])}
        self.sdk.create_schema(data)
        self.print(f"Created schema with id: {obj['id']}", data)


class Schemas(BasePipelinesCommand):
    """
    usage:
      okdata pipelines schemas [--id=<id>] [options]
      okdata pipelines schemas ls [options]
      okdata pipelines schemas create (<file> | -) [options]

    options:
      -d --debug
      --format=<format>
    """

    def __init__(self, sdk):
        super().__init__(sdk)
        self.sub_commands = [SchemasLs, SchemasCreate]

    def default(self):
        id = self.opt("id")
        if self.opt("help") or not id:
            return self.help()
        schema = self.sdk.get_schema(id)
        schema.schema = json.loads(schema.schema)
        self.print(f"Schema for: {id}", schema.__dict__)
        return None
