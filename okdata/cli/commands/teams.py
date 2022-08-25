from operator import itemgetter

from okdata.sdk.team.client import TeamClient

from okdata.cli.command import BASE_COMMAND_OPTIONS, BaseCommand
from okdata.cli.output import create_output


class TeamsCommand(BaseCommand):
    __doc__ = f"""Oslo :: Teams

Usage:
  okdata teams ls [--my] [options]

Examples:
  okdata teams ls
  okdata teams ls --my

Options:{BASE_COMMAND_OPTIONS}
    """

    def __init__(self):
        super().__init__()
        self.client = TeamClient(env=self.opt("env"))

    def handler(self):
        if self.cmd("ls"):
            self.ls(self.opt("my"))

    def ls(self, my):
        teams = self.client.get_teams(
            include=None if my else "all", has_role="origo-team"
        )
        out = create_output(self.opt("format"), "teams_config.json")
        out.add_rows(sorted(teams, key=itemgetter("name")))
        self.print("{} teams:".format("My" if my else "All"), out)
