import re
from unittest.mock import ANY

from conftest import set_argv
from okdata.cli.commands.permissions import PermissionsCommand

DATASETS_CMD_QUAL = f"{PermissionsCommand.__module__}.{PermissionsCommand.__name__}"

my_permissions = {
    "okdata:dataset:my-dataset-1": {
        "scopes": [
            "okdata:dataset:read",
        ]
    },
    "okdata:dataset:my-dataset-2": {
        "scopes": [
            "okdata:dataset:admin",
        ]
    },
}

permissions = [
    {
        "resource_name": "okdata:dataset:my-dataset",
        "description": "",
        "scope": "okdata:dataset:read",
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
    assert re.search("okdata:dataset:my-dataset-1.*okdata:dataset:read", out)
    assert re.search("okdata:dataset:my-dataset-2.*okdata:dataset:admin", out)


def test_list_permissions(mocker, mock_print):
    cmd = make_cmd(mocker, "ls", "okdata:dataset:my-dataset")
    cmd.handler()
    mock_print.assert_called_once()
    output = str(mock_print.mock_calls[0][1][1])
    assert re.search("foo.*okdata:dataset:read", output)


def test_add_user(mocker):
    cmd = make_cmd(
        mocker, "add", "okdata:dataset:my-dataset", "foo", "okdata:dataset:read"
    )
    cmd.handler()
    cmd.client.update_permission.assert_called_once_with(
        "okdata:dataset:my-dataset", "okdata:dataset:read", add_users=[ANY]
    )
    user = cmd.client.update_permission.mock_calls[0].kwargs["add_users"][0]
    assert user.user_id == "foo"
    assert user.user_type == "user"


def test_add_client(mocker):
    cmd = make_cmd(
        mocker,
        "add",
        "okdata:dataset:my-dataset",
        "bar",
        "okdata:dataset:read",
        "--client",
    )
    cmd.handler()
    cmd.client.update_permission.assert_called_once_with(
        "okdata:dataset:my-dataset", "okdata:dataset:read", add_users=[ANY]
    )
    user = cmd.client.update_permission.mock_calls[0][2]["add_users"][0]
    assert user.user_id == "bar"
    assert user.user_type == "client"


def test_add_team(mocker):
    cmd = make_cmd(
        mocker,
        "add",
        "okdata:dataset:my-dataset",
        "baz",
        "okdata:dataset:read",
        "--team",
    )
    cmd.handler()
    cmd.client.update_permission.assert_called_once_with(
        "okdata:dataset:my-dataset", "okdata:dataset:read", add_users=[ANY]
    )
    user = cmd.client.update_permission.mock_calls[0][2]["add_users"][0]
    assert user.user_id == "baz"
    assert user.user_type == "team"


def test_remove_user(mocker):
    cmd = make_cmd(mocker, "rm", "okdata:dataset:my-dataset", "foo")
    cmd.handler()
    cmd.client.update_permission.assert_called_once_with(
        "okdata:dataset:my-dataset", "okdata:dataset:read", remove_users=[ANY]
    )
    user = cmd.client.update_permission.mock_calls[0][2]["remove_users"][0]
    assert user.user_id == "foo"
    assert user.user_type == "user"


def test_remove_user_nothing_to_remove(mocker):
    cmd = make_cmd(mocker, "rm", "okdata:dataset:my-dataset", "foobar")
    cmd.handler()
    cmd.client.update_permission.assert_not_called()


def test_remove_user_scope(mocker):
    cmd = make_cmd(
        mocker, "rm", "okdata:dataset:my-dataset", "foo", "okdata:dataset:write"
    )
    cmd.handler()
    cmd.client.update_permission.assert_called_once_with(
        "okdata:dataset:my-dataset", "okdata:dataset:write", remove_users=[ANY]
    )
    user = cmd.client.update_permission.mock_calls[0][2]["remove_users"][0]
    assert user.user_id == "foo"
    assert user.user_type == "user"


def test_remove_client(mocker):
    cmd = make_cmd(mocker, "rm", "okdata:dataset:my-dataset", "bar", "--client")
    cmd.handler()
    cmd.client.update_permission.assert_called_once_with(
        "okdata:dataset:my-dataset", "okdata:dataset:read", remove_users=[ANY]
    )
    user = cmd.client.update_permission.mock_calls[0][2]["remove_users"][0]
    assert user.user_id == "bar"
    assert user.user_type == "client"


def test_remove_team(mocker):
    cmd = make_cmd(mocker, "rm", "okdata:dataset:my-dataset", "baz", "--team")
    cmd.handler()
    cmd.client.update_permission.assert_called_once_with(
        "okdata:dataset:my-dataset", "okdata:dataset:read", remove_users=[ANY]
    )
    user = cmd.client.update_permission.mock_calls[0][2]["remove_users"][0]
    assert user.user_id == "baz"
    assert user.user_type == "team"
