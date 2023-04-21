from operator import itemgetter

from okdata.sdk.team.client import TeamClient

from okdata.cli import MAINTAINER
from okdata.cli.command import BASE_COMMAND_OPTIONS, BaseCommand
from okdata.cli.commands.teams.questions import NoTeamError
from okdata.cli.commands.teams.util import (
    member_representation,
    sorted_member_list,
)
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
        teams = self.client.get_teams(
            include=None if my else "all", has_role="origo-team"
        )
        out = create_output(self.opt("format"), "teams_config.json")
        out.add_rows(sorted(teams, key=itemgetter("name")))
        self.print("{} teams:".format("My" if my else "All"), out)

    def edit(self):
        try:
            config = edit_team_wizard(self.client)
        except NoTeamError:
            self.print(
                "We haven't yet registered you as member of any Origo team. "
                f"Please contact {MAINTAINER} to get it done."
            )
            return

        if config["attribute"] == "name":
            self.client.update_team_name(config["team_id"], config["team_name"])
        else:
            self.client.update_team_attribute(
                config["team_id"], config["attribute"], config["attribute_value"]
            )
        self.print("Done!")

    def list_members(self, my):
        try:
            config = list_members_wizard(self.client, my)
            members = self.client.get_team_members(config["team_id"])
        except NoTeamError:
            self.print(
                "We haven't yet registered you as member of any Origo team. "
                f"Please contact {MAINTAINER} to get it done."
                if my
                else "No teams exist yet."
            )
            return

        out = create_output(self.opt("format"), "team_members_config.json")

        out.add_rows(sorted_member_list(members))
        self.print("Team members", out)

    def add_member(self):
        try:
            config = add_member_wizard(self.client)
        except NoTeamError:
            self.print(
                "We haven't yet registered you as member of any Origo team. "
                f"Please contact {MAINTAINER} to get it done."
            )
            return

        user = self.client.get_user_by_username(config["username"])
        team_members = [
            m["username"] for m in self.client.get_team_members(config["team_id"])
        ]

        if user["username"] in team_members:
            self.print(
                "User {} is already a member of this team.".format(
                    member_representation(user)
                )
            )
            return

        self.confirm_to_continue(
            "Add {} to the team?".format(member_representation(user))
        )

        self.client.update_team_members(
            config["team_id"], team_members + [user["username"]]
        )
        self.print("Done!")

    def remove_member(self):
        try:
            config = remove_member_wizard(self.client)
        except NoTeamError:
            self.print(
                "We haven't yet registered you as member of any Origo team. "
                f"Please contact {MAINTAINER} to get it done."
            )
            return

        team_members = self.client.get_team_members(config["team_id"])
        members_to_remove, members_to_keep = [], []
        for member in team_members:
            if member["username"] in config["usernames"]:
                members_to_remove.append(member)
            else:
                members_to_keep.append(member)

        if len(members_to_keep) == 0:
            self.confirm_to_continue(
                "You are about to delete all members from the team, including "
                "yourself. It will not be possible to edit this team any "
                "further without being re-added by a systems administrator."
            )
        else:
            self.confirm_to_continue(
                "Remove the following member{} from the team?\n - {}".format(
                    "s" if len(members_to_remove) > 1 else "",
                    "\n - ".join(
                        [
                            member_representation(m)
                            for m in sorted_member_list(members_to_remove)
                        ]
                    ),
                )
            )

        self.client.update_team_members(
            config["team_id"], [m["username"] for m in members_to_keep]
        )
        self.print("Done!")
