import re
from unittest.mock import ANY

from conftest import set_argv
from okdata.cli.commands.permissions import PermissionsCommand

my_permissions = {
    "maskinporten:client:test-client-1": {
        "scopes": [
            "maskinporten:client:read",
        ]
    },
    "maskinporten:client:test-client-2": {
        "scopes": [
            "maskinporten:client:write",
        ]
    },
}

permissions = [
    {
        "resource_name": "maskinporten:client:test-client",
        "description": "",
        "scope": "maskinporten:client:read",
        "users": ["foo"],
        "clients": ["bar"],
        "teams": ["baz"],
    },
]


def make_cmd(mocker, *args):
    set_argv("permissions", *args)
    cmd = PermissionsCommand()
    mocker.patch.object(cmd, "client")
    cmd.client.get_my_permissions.return_value = my_permissions
    cmd.client.get_permissions.return_value = permissions
    return cmd


def test_list_my_permissions(mocker, mock_print):
    cmd = make_cmd(mocker, "ls")
    cmd.handler()
    mock_print.assert_called_once()
    out = str(mock_print.mock_calls[0].args[1])
    assert re.search("maskinporten:client:test-client-1.*maskinporten:client:read", out)
    assert re.search(
        "maskinporten:client:test-client-2.*maskinporten:client:write", out
    )


def test_list_permissions(mocker, mock_print):
    cmd = make_cmd(mocker, "ls", "maskinporten:client:test-client")
    cmd.handler()
    mock_print.assert_called_once()
    output = str(mock_print.mock_calls[0][1][1])
    assert re.search("foo.*maskinporten:client:read", output)


def test_add_user(mocker):
    cmd = make_cmd(
        mocker,
        "add",
        "maskinporten:client:test-client",
        "foo",
        "maskinporten:client:read",
    )
    cmd.handler()
    cmd.client.update_permission.assert_called_once_with(
        "maskinporten:client:test-client", "maskinporten:client:read", add_users=[ANY]
    )
    user = cmd.client.update_permission.mock_calls[0].kwargs["add_users"][0]
    assert user.user_id == "foo"
    assert user.user_type == "user"


def test_add_client(mocker):
    cmd = make_cmd(
        mocker,
        "add",
        "maskinporten:client:test-client",
        "bar",
        "maskinporten:client:read",
        "--client",
    )
    cmd.handler()
    cmd.client.update_permission.assert_called_once_with(
        "maskinporten:client:test-client", "maskinporten:client:read", add_users=[ANY]
    )
    user = cmd.client.update_permission.mock_calls[0][2]["add_users"][0]
    assert user.user_id == "bar"
    assert user.user_type == "client"


def test_add_team(mocker):
    cmd = make_cmd(
        mocker,
        "add",
        "maskinporten:client:test-client",
        "baz",
        "maskinporten:client:read",
        "--team",
    )
    cmd.handler()
    cmd.client.update_permission.assert_called_once_with(
        "maskinporten:client:test-client", "maskinporten:client:read", add_users=[ANY]
    )
    user = cmd.client.update_permission.mock_calls[0][2]["add_users"][0]
    assert user.user_id == "baz"
    assert user.user_type == "team"


def test_remove_user(mocker):
    cmd = make_cmd(mocker, "rm", "maskinporten:client:test-client", "foo")
    cmd.handler()
    cmd.client.update_permission.assert_called_once_with(
        "maskinporten:client:test-client", "__all__", remove_users=[ANY]
    )
    user = cmd.client.update_permission.mock_calls[0][2]["remove_users"][0]
    assert user.user_id == "foo"
    assert user.user_type == "user"


def test_remove_user_scope(mocker):
    cmd = make_cmd(
        mocker,
        "rm",
        "maskinporten:client:test-client",
        "foo",
        "maskinporten:client:write",
    )
    cmd.handler()
    cmd.client.update_permission.assert_called_once_with(
        "maskinporten:client:test-client",
        "maskinporten:client:write",
        remove_users=[ANY],
    )
    user = cmd.client.update_permission.mock_calls[0][2]["remove_users"][0]
    assert user.user_id == "foo"
    assert user.user_type == "user"


def test_remove_client(mocker):
    cmd = make_cmd(mocker, "rm", "maskinporten:client:test-client", "bar", "--client")
    cmd.handler()
    cmd.client.update_permission.assert_called_once_with(
        "maskinporten:client:test-client", "__all__", remove_users=[ANY]
    )
    user = cmd.client.update_permission.mock_calls[0][2]["remove_users"][0]
    assert user.user_id == "bar"
    assert user.user_type == "client"


def test_remove_team(mocker):
    cmd = make_cmd(mocker, "rm", "maskinporten:client:test-client", "baz", "--team")
    cmd.handler()
    cmd.client.update_permission.assert_called_once_with(
        "maskinporten:client:test-client", "__all__", remove_users=[ANY]
    )
    user = cmd.client.update_permission.mock_calls[0][2]["remove_users"][0]
    assert user.user_id == "baz"
    assert user.user_type == "team"
