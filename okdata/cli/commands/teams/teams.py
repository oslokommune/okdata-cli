from operator import itemgetter

from okdata.sdk.team.client import TeamClient
from requests.exceptions import HTTPError

from okdata.cli.command import BASE_COMMAND_OPTIONS, BaseCommand
from okdata.cli.commands.teams.questions import NoTeamError
from okdata.cli.commands.teams.wizards import edit_team_wizard
from okdata.cli.output import create_output


class TeamsCommand(BaseCommand):
    __doc__ = f"""Oslo :: Teams

Usage:
  okdata teams ls [--my] [options]
  okdata teams edit [options]

Examples:
  okdata teams ls
  okdata teams ls --my
  okdata teams edit

Options:{BASE_COMMAND_OPTIONS}
    """

    def __init__(self):
        super().__init__()
        self.client = TeamClient(env=self.opt("env"))

    def handler(self):
        if self.cmd("ls"):
            self.ls(self.opt("my"))
        if self.cmd("edit"):
            self.edit()

    def ls(self, my):
        try:
            teams = self.client.get_teams(
                include=None if my else "all", has_role="origo-team"
            )
        except HTTPError as e:
            message = e.response.json()["message"]
            self.print(f"Something went wrong: {message}")
            return

        out = create_output(self.opt("format"), "teams_config.json")
        out.add_rows(sorted(teams, key=itemgetter("name")))
        self.print("{} teams:".format("My" if my else "All"), out)

    def edit(self):
        try:
            config = edit_team_wizard(self.client)
        except NoTeamError:
            self.print(
                "We haven't yet registered you as member of any Origo team. "
                "Please contact Datapatruljen to get it done."
            )
            return

        try:
            if "team_name" in config:
                self.client.update_team_name(
                    config["team_id"],
                    config["team_name"],
                )
            else:
                self.client.update_team_attribute(
                    config["team_id"],
                    config["attribute"],
                    config["attribute_value"],
                )
            self.print("Done!")
        except HTTPError as e:
            message = e.response.json()["message"]
            self.print(f"Something went wrong: {message}")
