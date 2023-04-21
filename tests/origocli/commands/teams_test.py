from unittest.mock import ANY, MagicMock

import pytest
from requests import HTTPError

from conftest import set_argv
from okdata.cli.commands.teams import teams
from okdata.cli.commands.teams.questions import NoTeamError

mock_teams = [
    {"id": "e38a9617-4f1d-4f1c-898c-ead94eb54184", "name": "team1"},
    {"id": "0c646d75-e9b3-47e9-8897-79a44f341577", "name": "team3"},
]

mock_members = [
    {
        "username": "janedoe",
        "name": "Jane Doe",
        "email": None,
    },
    {
        "username": "homersimpson",
        "name": "Homer Simpson",
        "email": None,
    },
    {
        "username": "misty",
        "name": "Kasumi Mist",
        "email": None,
    },
]


def make_cmd(mocker, *args):
    set_argv("teams", *args)
    cmd = teams.TeamsCommand()
    mocker.patch.object(cmd, "client")
    mocker.patch.object(cmd, "confirm_to_continue")
    mocker.patch.object(teams, "list_members_wizard")
    mocker.patch.object(teams, "add_member_wizard")
    mocker.patch.object(teams, "remove_member_wizard")
    cmd.client.get_teams.return_value = mock_teams
    cmd.client.get_team_members.return_value = mock_members[0:2]
    cmd.client.get_user_by_username.return_value = mock_members[2]
    return cmd


def test_list_members(mocker, mock_print):
    cmd = make_cmd(mocker, "list-members", "--format=json")
    config = {"team_id": "team1"}
    teams.list_members_wizard.return_value = config

    cmd.handler()

    teams.list_members_wizard.assert_called_once_with(ANY, False)
    cmd.client.get_team_members.assert_called_once_with(config["team_id"])
    out = mock_print.mock_calls[0][1][1].out
    assert list(map(lambda m: m["name"], out)) == [
        "Homer Simpson",
        "Jane Doe",
    ]


def test_list_members_my_teams(mocker, mock_print):
    cmd = make_cmd(mocker, "list-members", "--my", "--format=json")
    config = {"team_id": "team1"}
    teams.list_members_wizard.return_value = config

    cmd.handler()

    teams.list_members_wizard.assert_called_once_with(ANY, True)
    cmd.client.get_team_members.assert_called_once_with(config["team_id"])


def test_list_members_no_teams(mocker, mock_print):
    cmd = make_cmd(mocker, "list-members", "--format=json")
    teams.list_members_wizard.side_effect = NoTeamError()

    cmd.handler()

    mock_print.assert_called_once()
    assert mock_print.mock_calls[0][1][0] == "No teams exist yet."
    cmd.client.add_team_member.assert_not_called()


def test_add_team_member(mocker, mock_print):
    cmd = make_cmd(mocker, "add-member")
    config = {"team_id": "team1", "username": "misty"}
    teams.add_member_wizard.return_value = config

    cmd.handler()

    teams.add_member_wizard.assert_called_once()
    target_members = [u["username"] for u in mock_members]
    assert config["username"] in target_members
    cmd.client.update_team_members.assert_called_once_with(
        config["team_id"], target_members
    )
    assert mock_print.mock_calls[0][1][0] == "Done!"


def test_add_team_member_already_member(mocker, mock_print):
    cmd = make_cmd(mocker, "add-member")
    cmd.client.get_user_by_username.return_value = mock_members[0]
    config = {"team_id": "team1", "username": "janedoe"}
    teams.add_member_wizard.return_value = config

    cmd.handler()

    teams.add_member_wizard.assert_called_once()
    cmd.client.update_team_members.assert_not_called()
    assert (
        mock_print.mock_calls[0][1][0]
        == "User Jane Doe (janedoe) is already a member of this team."
    )


def test_add_team_member_no_team(mocker, mock_print):
    cmd = make_cmd(mocker, "add-member")
    teams.add_member_wizard.side_effect = NoTeamError()

    cmd.handler()

    mock_print.assert_called_once()
    message = "We haven't yet registered you as member of any Origo team."
    assert message in mock_print.mock_calls[0][1][0]
    cmd.client.update_team_members.assert_not_called()


def test_add_team_member_with_http_error(mocker, mock_print):
    cmd = make_cmd(mocker, "add-member")
    config = {"team_id": "team1", "username": "foo"}
    teams.add_member_wizard.return_value = config
    error_message = "User not found"
    http_error = HTTPError()
    http_error.response = MagicMock()
    http_error.response.json = lambda: {"message": error_message}
    cmd.client.get_user_by_username.side_effect = http_error

    with pytest.raises(HTTPError):
        cmd.handler()

    cmd.client.update_team_members.assert_not_called()


def test_remove_team_member(mocker, mock_print):
    cmd = make_cmd(mocker, "remove-member")
    team_id = "team1"
    config = {"team_id": team_id, "usernames": ["homersimpson"]}
    teams.remove_member_wizard.return_value = config

    cmd.handler()

    teams.remove_member_wizard.assert_called_once()
    cmd.client.update_team_members.assert_called_once_with(
        config["team_id"], ["janedoe"]
    )
    assert mock_print.mock_calls[0][1][0] == "Done!"


def test_remove_all_team_members(mocker, mock_print):
    cmd = make_cmd(mocker, "remove-member")
    team_id = "team1"
    config = {"team_id": team_id, "usernames": ["homersimpson", "misty", "janedoe"]}
    teams.remove_member_wizard.return_value = config

    cmd.handler()

    teams.remove_member_wizard.assert_called_once()
    cmd.confirm_to_continue.assert_called_once()
    cmd.client.update_team_members.assert_called_once_with(config["team_id"], [])
    assert mock_print.mock_calls[0][1][0] == "Done!"
