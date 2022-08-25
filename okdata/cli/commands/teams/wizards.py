from okdata.cli.commands.teams.questions import (
    q_attribute,
    q_attribute_value,
    q_team,
    q_team_name,
)
from okdata.cli.commands.wizard import run_questionnaire


def edit_team_wizard(team_client):
    choices = run_questionnaire(
        q_team(team_client),
        q_attribute(team_client),
        q_team_name(),
        q_attribute_value(),
    )
    return {
        "team_id": choices["team_id"],
        "attribute": choices["attribute"][0],
        "team_name": choices.get("team_name"),
        "attribute_value": choices.get("attribute_value"),
    }


def list_members_wizard(team_client, my):
    choices = run_questionnaire(q_team(team_client, my))
    return {"team_id": choices["team_id"]}
