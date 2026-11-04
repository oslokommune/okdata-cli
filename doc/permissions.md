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
resources. We use `user`, `scope`, and `resource_name` to give the
who/what/which parts, respectively, so a permission can be viewed as a triplet:

    <user>, <scope>, <resource_name>

Meaning `<user>` is allowed to do `<scope>` on `<resource_name>`. For instance:

    janedoe, maskinporten:client:read, maskinporten:client:test-6970b743-5075-3f1a-3d35-ac84ea3dc79b

Meaning that the user `janedoe` is allowed to perform read operations on the
public service client with ID `6970b743-5075-3f1a-3d35-ac84ea3dc79b` in the
`test` environment.

### User types

The `<user>` part can be either a user ID (username), a team ID, which grants
the permission to every member of the given team, or the ID of a machine user (a
*client* in Keycloak terms, not to be confused with the public service clients
described below), in case you've been assigned one by Dataspeilet.

### Scopes

Scopes consist of three parts separated by colons: a namespace, a resource type,
and the permission itself. Permissions currently apply to clients for public
services (Maskinporten and ID-porten), which are managed with the [`pubs`
commands](pubs.md). The available scopes are:

- `maskinporten:client:read`, allowing the user to see the given client, list
  its keys, and view its audit log.

- `maskinporten:client:write`, allowing the user to create and delete keys for
  the given client, and to delete the client itself.

Both scopes are granted to the owning team when a client is created.

### Resource names

Resource names also consist of three parts separated by colons: a namespace, a
resource type, and the resource ID itself. For public service clients the
resource type is `maskinporten:client`, and the resource ID is the client's
environment (`test` or `prod`) followed by a dash and the client ID:

    maskinporten:client:<env>-<client_id>

The client ID is shown by `okdata pubs list-clients`.

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
okdata permissions ls maskinporten:client:test-6970b743-5075-3f1a-3d35-ac84ea3dc79b
```

This will list every permission associated with the given client. Note that this
requires admin rights on the resource, see [who can manage
permissions](#who-can-manage-permissions) below.

## Granting and revoking permissions

The commands for granting and revoking permissions to and from users, are:

```bash
okdata permissions add <resource_name> <user> [<scope>]
okdata permissions rm <resource_name> <user> [<scope>]
```

The format of `resource_name`, `user`, and `scope` is explained in the [previous
section](#what-are-permissions).

Here is an example where the user `janedoe` is given read access to the client
`6970b743-5075-3f1a-3d35-ac84ea3dc79b` in the `test` environment:

```bash
okdata permissions add maskinporten:client:test-6970b743-5075-3f1a-3d35-ac84ea3dc79b janedoe maskinporten:client:read
```

And to revoke that same permission:

```bash
okdata permissions rm maskinporten:client:test-6970b743-5075-3f1a-3d35-ac84ea3dc79b janedoe maskinporten:client:read
```

The `scope` parameter is optional in both commands. When omitted, all
permissions are granted or revoked for the user on the given resource.

Both commands support additional `--team` and `--client` flags, which are used
when the given user ID belongs to a team or a machine user, instead of a person
user. For instance, to give every member of a team write access to the same
client:

```bash
okdata permissions add maskinporten:client:test-6970b743-5075-3f1a-3d35-ac84ea3dc79b <team_id> maskinporten:client:write --team
```

### Who can manage permissions

Listing the permissions for a resource, as well as granting and revoking them,
requires admin rights on that resource. Teams are not granted admin rights on
their public service clients, so if you need to change who has access to one of
your clients, get in touch with Dataspeilet.
