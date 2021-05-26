from operator import itemgetter

from okdata.sdk.permission.client import PermissionClient
from okdata.sdk.permission.user_types import Client, Team, User

from okdata.cli.command import BASE_COMMAND_OPTIONS, BaseCommand
from okdata.cli.output import create_output


class PermissionsCommand(BaseCommand):
    __doc__ = f"""Oslo :: Permissions

Usage:
  okdata permissions ls [<resource_name>] [--format=<format> --env=<env>]
  okdata permissions add <resource_name> <user> <scope> [--team | --client] [--env=<env>]
  okdata permissions rm <resource_name> <user> [<scope>] [--team | --client] [--env=<env>]

Examples:
  okdata permissions ls
  okdata permissions ls okdata:dataset:my-dataset
  okdata permissions add okdata:dataset:my-dataset janedoe okdata:dataset:read
  okdata permissions rm okdata:dataset:my-dataset janedoe
  okdata permissions rm okdata:dataset:my-dataset janedoe okdata:dataset:write

Options:{BASE_COMMAND_OPTIONS}
  --history
    """

    def __init__(self):
        super().__init__()
        self.client = PermissionClient(env=self.opt("env"))

    def handler(self):
        resource_name = self.arg("resource_name")

        if self.cmd("ls"):
            if resource_name:
                self.list_permissions(resource_name)
            else:
                self.list_my_permissions()
        elif self.cmd("add") or self.cmd("rm"):
            user = self.arg("user")
            scope = self.arg("scope")

            if self.opt("team"):
                user_class = Team
            elif self.opt("client"):
                user_class = Client
            else:
                user_class = User

            fmt_args = [
                f"'{scope}'" if scope else "every permission",
                resource_name,
                user_class.__name__.lower(),
                user,
            ]
            if self.cmd("add"):
                self.add_user(resource_name, user_class(user), scope)
                self.print("Granted {} on '{}' for {} '{}'".format(*fmt_args))
            else:
                self.remove_user(resource_name, user_class(user), scope)
                self.print("Revoked {} on '{}' for {} '{}'".format(*fmt_args))

    def list_my_permissions(self):
        """Print all permissions for the current user."""
        permissions = self.client.get_my_permissions()
        results = [
            {
                "resource_name": resource_name,
                "scopes": ", ".join(sorted(data["scopes"])),
            }
            for resource_name, data in permissions.items()
        ]
        out = create_output(self.opt("format"), "my_permissions_config.json")
        out.add_rows(sorted(results, key=itemgetter("resource_name")))
        self.print("My permissions", out)

    def list_permissions(self, resource_name):
        """Print all permissions associated with `resource_name`."""
        permissions = self.client.get_permissions(resource_name)
        reverse_index = {}
        for perm in permissions:
            for user_type in ["teams", "users", "clients"]:
                for entry in perm[user_type]:
                    reverse_index.setdefault((entry, user_type), []).append(
                        perm["scope"]
                    )
        results = []
        for entry, scopes in reverse_index.items():
            results.append(
                {
                    "user_name": entry[0],
                    "user_type": entry[1][:-1].capitalize(),
                    "scopes": ", ".join(sorted(scopes)),
                }
            )
        out = create_output(self.opt("format"), "permissions_config.json")
        out.add_rows(sorted(results, key=itemgetter("user_type", "user_name")))
        self.print(f"Permissions for '{resource_name}'", out)

    def add_user(self, resource_name, user, scope):
        """Grant `scope` on `resource_name` to `user`."""
        self.client.update_permission(resource_name, scope, add_users=[user])

    def remove_user(self, resource_name, user, scope=None):
        """Revoke `scope` on `resource_name` for `user`.

        When `scope` is unspecified, revoke every permission on `resource_name`
        for `user`.
        """
        if scope:
            self.client.update_permission(resource_name, scope, remove_users=[user])
        else:
            for permission in self.client.get_permissions(resource_name):
                if user.user_id in permission[f"{user.user_type}s"]:
                    self.client.update_permission(
                        resource_name, permission["scope"], remove_users=[user]
                    )
