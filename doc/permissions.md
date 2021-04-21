# Permissions

To see all operations available on permissions:

```bash
okdata permissions -h
```

Contents:
* [What are permissions](#what-are-permissions)
* [Listing permissions](#listing-permissions)
* [Granting and revoking permissions](#granting-and-revoking-permissions)

## What are permissions

*Permissions* allow fine grained control over *who* can do *what* with *which*
resources in the dataplatform. We use `user`, `scope`, and `resource_name` to
give the who/what/which parts, respectively, so a permission can be viewed as a
triplet:

    <user>, <scope>, <resource_name>

Meaning `<user>` is allowed to do `<scope>` on `<resource_name>`. For instance:

    janedoe, okdata:dataset:read, okdata:dataset:my-dataset

Meaning that the user `janedoe` is allowed to perform read operations on the
dataset named `my-dataset`.

### User types

The `<user>` part can be either a user ID (username), a team ID, which grants
the permission to every member of the given team, or a client ID, in case you've
been assigned a machine client user by the dataplatform team.

### Scopes

Scopes consist of three parts separated by colons: a namespace, a resource type,
and the permission itself. Permissions currently only apply to datasets, though
this might be extended in the future. For now, the available scopes are:

- `okdata:dataset:admin`, allowing the user to modify the permissions for the
  given dataset.

- `okdata:dataset:read`, allowing the user to see/download data from the given
  dataset.

- `okdata:dataset:update`, allowing the user to change metadata for the given
  dataset, like its title and description.

- `okdata:dataset:write`, allowing the user to write/upload new data to the
  given dataset.

### Resource names

Resource names also consist of three parts separated by colons: a namespace, a
resource type, and the resource ID itself. The only resource type currently
available is `okdata:dataset`, and the resource ID becomes the ID of the
dataset.

## Listing permissions

The following command lists all permissions tied to the current user:

```bash
okdata permissions ls
```

To list all permissions for a specific resource, the following command is used:

```bash
okdata permissions ls <resource_name>
```

For instance:

```bash
okdata permissions ls okdata:dataset:my-dataset
```

This will list every permission associated with the dataset `my-dataset`.

## Granting and revoking permissions

The commands for granting and revoking permissions to and from users, are:

```bash
okdata permissions add <resource_name> <user> <scope>
okdata permissions rm <resource_name> <user> [<scope>]
```

The format of `resource_name`, `user`, and `scope` is explained in the [previous
section](#what-are-permissions).

Here is an example where the user `janedoe` is given read access to the dataset
`my-dataset`:

```bash
okdata permissions add okdata:dataset:my-dataset janedoe okdata:dataset:read
```

And to revoke that same permission:

```bash
okdata permissions rm okdata:dataset:my-dataset janedoe okdata:dataset:read
```

The `scope` parameter is optional for `rm`. When omitted, all permissions for
the user on the given resource are revoked.

Both commands support additional `--team` and `--client` flags, which are used
when the given user ID belongs to a team or a machine user, instead of a person
user.
