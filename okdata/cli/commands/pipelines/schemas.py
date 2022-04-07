import json

from okdata.cli.command import BaseCommand
from okdata.cli.output import create_output


class SchemasLs(BaseCommand):
    """okdata::pipelines::ls
    usage:
      okdata pipelines schemas ls [options]

    options:
      -d --debug
      --format=<format>
    """

    def handler(self):
        out = create_output(
            self.opt("format"), "pipelines_instances_schemas_config.json"
        )
        schemas = self.sdk.get_schemas()
        out.add_rows(schemas)
        self.print("List of Schemas available", out)


class SchemasCreate(BaseCommand):
    """
    usage:
      okdata pipelines schemas create - [options]
      okdata pipelines schemas create <file> [options]

    options:
      -d --debug
      --format=<format>
    """

    def handler(self):
        content = self.handle_input()
        obj = json.loads(content)
        data = {"id": obj["id"], "type": "schema", "schema": json.dumps(obj["schema"])}
        self.sdk.create_schema(data)
        self.print(f"Created schema with id: {obj['id']}", data)


class Schemas(BaseCommand):
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

    def handler(self):
        id = self.opt("id")
        if self.opt("help") or not id:
            return self.help()
        schema = self.sdk.get_schema(id)
        schema.schema = json.loads(schema.schema)
        self.print(f"Schema for: {id}", schema.__dict__)
        return None
