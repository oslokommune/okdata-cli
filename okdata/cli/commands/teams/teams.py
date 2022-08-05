from operator import itemgetter

from okdata.sdk.team.client import TeamClient
from requests.exceptions import HTTPError

from okdata.cli.command import BASE_COMMAND_OPTIONS, BaseCommand
from okdata.cli.commands.teams.questions import NoTeamError
from okdata.cli.commands.teams.wizards import (
    add_member_wizard,
    edit_team_wizard,
    list_members_wizard,
    remove_member_wizard,
)
from okdata.cli.output import create_output


class TeamsCommand(BaseCommand):
    __doc__ = f"""Oslo :: Teams

Usage:
  okdata teams ls [--my] [options]
  okdata teams edit [options]
  okdata teams list-members [--my] [options]
  okdata teams add-member [options]
  okdata teams remove-member [options]

Examples:
  okdata teams ls
  okdata teams ls --my
  okdata teams edit
  okdata teams list-members --my
  okdata teams add-member
  okdata teams remove-member

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
        if self.cmd("list-members"):
            self.list_members(self.opt("my"))
        if self.cmd("add-member"):
            self.add_member()
        if self.cmd("remove-member"):
            self.remove_member()

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

    def list_members(self, my):
        try:
            config = list_members_wizard(self.client, my)
            self._list_team_members(config["team_id"])
        except NoTeamError:
            self.print(
                "We haven't yet registered you as member of any Origo team. "
                "Please contact Datapatruljen to get it done."
                if my
                else "No teams exist yet."
            )

    def add_member(self):
        try:
            config = add_member_wizard(self.client)
        except NoTeamError:
            self.print(
                "We haven't yet registered you as member of any Origo team. "
                "Please contact Datapatruljen to get it done."
            )
            return

        try:
            self.client.add_team_member(
                config["team_id"],
                config["username"],
            )
        except HTTPError as e:
            message = e.response.json()["message"]
            self.print(f"Something went wrong: {message}")
            return

        self.print(f"User {config['username']} was added to the team!")
        self._list_team_members(config["team_id"])

    def remove_member(self):
        try:
            config = remove_member_wizard(self.client)
        except NoTeamError:
            self.print(
                "We haven't yet registered you as member of any Origo team. "
                "Please contact Datapatruljen to get it done."
            )
            return

        existing_members = self.client.get_team_members(config["team_id"])

        if len(config["usernames"]) == len(existing_members):
            self.confirm_to_continue(
                "You are about to delete all members from the team, including "
                "yourself. It will not be possible to edit this team any further "
                "without being re-added by a systems administrator."
            )

        for username in config["usernames"]:
            try:
                self.client.remove_team_member(config["team_id"], username)
            except HTTPError as e:
                message = e.response.json()["message"]
                self.print(f"Something went wrong: {message}")
                return
            self.print(f"User {username} was removed from the team!")
        self._list_team_members(config["team_id"])

    def _list_team_members(self, team_id):
        try:
            members = self.client.get_team_members(team_id)
        except HTTPError as e:
            message = e.response.json()["message"]
            self.print(f"Something went wrong: {message}")
            return

        out = create_output(self.opt("format"), "team_members_config.json")
        out.add_rows(sorted(members, key=itemgetter("name")))
        self.print("Team members", out)
