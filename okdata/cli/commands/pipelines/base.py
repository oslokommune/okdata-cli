from origocli.command import BaseCommand


class BasePipelinesCommand(BaseCommand):
    def __init__(self, sdk):
        super().__init__()
        self.sdk = sdk
        self.handler = self.default
