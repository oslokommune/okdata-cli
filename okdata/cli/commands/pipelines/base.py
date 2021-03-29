from okdata.cli.command import BaseCommand


class BasePipelinesCommand(BaseCommand):
    def __init__(self, sdk):
        super().__init__(sdk)
        self.handler = self.default
