from unittest.mock import ANY, call, MagicMock

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
        "id": "d4f72505-89b5-4f95-b6da-404309e225ef",
        "username": "janedoe",
        "name": "Jane Doe",
        "email": None,
    },
    {
        "id": "fe9cbf16-d047-428d-a23e-da5abce24aae",
        "username": "misty",
        "name": "Kasumi Mist",
        "email": None,
    },
    {
        "id": "f1d16b62-9ef2-4f2d-af4b-27997fca3a0d",
        "username": "homersimpson",
        "name": "Homer Simpson",
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
    cmd.client.get_team_members.return_value = mock_members
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
        "Kasumi Mist",
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
    config = {"team_id": "team1", "username": "janedoe"}
    teams.add_member_wizard.return_value = config

    cmd.handler()

    teams.add_member_wizard.assert_called_once()
    cmd.client.add_team_member.assert_called_once_with(
        config["team_id"],
        config["username"],
    )
    cmd.client.get_team_members.assert_called_once_with(config["team_id"])

    assert mock_print.call_count == 2
    assert mock_print.mock_calls[0][1][0] == "User janedoe was added to the team!"
    assert mock_print.mock_calls[1][1][0] == "Team members"


def test_add_team_member_no_team(mocker, mock_print):
    cmd = make_cmd(mocker, "add-member")
    teams.add_member_wizard.side_effect = NoTeamError()

    cmd.handler()

    mock_print.assert_called_once()
    message = "We haven't yet registered you as member of any Origo team."
    assert message in mock_print.mock_calls[0][1][0]
    cmd.client.add_team_member.assert_not_called()


def test_add_team_member_with_http_error(mocker, mock_print):
    cmd = make_cmd(mocker, "add-member")
    config = {"team_id": "team1", "username": "janedoe"}
    teams.add_member_wizard.return_value = config
    error_message = "User not found"
    http_error = HTTPError()
    http_error.response = MagicMock()
    http_error.response.json = lambda: {"message": error_message}
    cmd.client.add_team_member.side_effect = http_error

    cmd.handler()

    assert mock_print.called_once_with(f"Something went wrong: {error_message}")


def test_remove_team_member(mocker, mock_print):
    cmd = make_cmd(mocker, "remove-member")
    team_id = "team1"
    config = {"team_id": team_id, "usernames": ["misty"]}
    teams.remove_member_wizard.return_value = config

    cmd.handler()

    teams.remove_member_wizard.assert_called_once()
    cmd.client.remove_team_member.assert_called_once_with(team_id, "misty")

    assert mock_print.call_count == 2
    assert mock_print.mock_calls[0][1][0] == "User misty was removed from the team!"
    assert mock_print.mock_calls[1][1][0] == "Team members"


def test_remove_all_team_members(mocker, mock_print):
    cmd = make_cmd(mocker, "remove-member")
    team_id = "team1"
    config = {"team_id": team_id, "usernames": ["homersimpson", "misty", "janedoe"]}
    teams.remove_member_wizard.return_value = config

    cmd.handler()

    teams.remove_member_wizard.assert_called_once()
    cmd.confirm_to_continue.assert_called_once()
    cmd.client.remove_team_member.assert_has_calls(
        [
            call(team_id, "homersimpson"),
            call(team_id, "misty"),
            call(team_id, "janedoe"),
        ]
    )
