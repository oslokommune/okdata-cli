from questionary import Choice

from okdata.cli.commands.wizard import common_style


class NoTeamError(Exception):
    """Raised when the current user doesn't belong to any team."""

    pass


class NoTeamMembersError(Exception):
    """Raised when a team does not have any members."""

    pass


def q_team(team_client, my=True):
    def _team_choices():
        teams = team_client.get_teams(
            include=None if my else "all", has_role="origo-team"
        )

        if not teams:
            raise NoTeamError

        return [Choice(t["name"], t["id"]) for t in teams]

    return {
        **common_style,
        "type": "select",
        "name": "team_id",
        "message": "Team",
        "choices": _team_choices(),
    }


def q_attribute(team_client):
    def _attribute_choices(team_id):
        team = team_client.get_team(team_id)
        name = team["name"]
        email = (team["attributes"]["email"] or [""])[0]
        slack_url = (team["attributes"]["slack-url"] or [""])[0]

        return [
            Choice(f"Name: {name}", ("name", name)),
            Choice(f"Email: {email or '<unset>'}", ("email", email)),
            Choice(
                f"Slack channel: {slack_url or '<unset>'}",
                ("slack-url", slack_url),
            ),
        ]

    return {
        **common_style,
        "type": "select",
        "name": "attribute",
        "message": "Edit what?",
        "choices": lambda x: _attribute_choices(x["team_id"]),
    }


def q_team_name():
    return {
        **common_style,
        "default": lambda x: x["attribute"][1],
        "type": "text",
        "name": "team_name",
        "message": "Team name",
        "when": lambda x: x["attribute"][0] == "name",
        "validate": lambda t: bool(t) or "Can't be empty",
    }


def q_attribute_value():
    return {
        **common_style,
        "default": lambda x: x["attribute"][1] or "",
        "type": "text",
        "name": "attribute_value",
        "message": "New value",
        "when": lambda x: x["attribute"][0] != "name",
    }


def q_username():
    return {
        **common_style,
        "type": "text",
        "name": "username",
        "message": "Username (ident)",
        "validate": lambda t: bool(t) or "Can't be empty",
    }


def q_members(team_client):
    def _team_member_choices(team_id):
        members = team_client.get_team_members(team_id)

        if not members:
            raise NoTeamMembersError

        return [
            Choice(
                f"{m['name']} ({m['username']})" if m["name"] else m["username"],
                m["username"],
            )
            for m in sorted(
                members,
                key=lambda u: (not u["name"], u["name"] or "", u["username"]),
            )
        ]

    return {
        **common_style,
        "type": "checkbox",
        "name": "usernames",
        "message": "Member(s)",
        "choices": lambda x: _team_member_choices(x["team_id"]),
        "validate": lambda x: bool(x) or "Select at least one team member",
    }
