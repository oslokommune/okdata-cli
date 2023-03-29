# Public registers

Commands related to accessing public registers are grouped under the `pubreg`
command prefix. Run the following command to see a list of all available
`pubreg` commands:

```sh
okdata pubreg -h
```

Contents:
* [Prerequisites](#prerequisites)
* [Creating a client](#creating-a-client)
* [Listing clients](#listing-clients)
* [Deleting a client](#deleting-a-client)
* [Creating a client key](#creating-a-client-key)
* [Rotating a client key](#rotating-a-client-key)
* [Listing client keys](#listing-client-keys)
* [Deleting a client key](#deleting-a-client-key)
* [Viewing a client's audit log](#viewing-a-clients-audit-log)

## Prerequisites

Make sure you've got the right legal basis before accessing public registry
data. Read more about this in our [guidelines for accessing public
registers](https://github.com/oslokommune/dataplattform/blob/master/origo/registerdata/offentlige-registerdata.md).

## Creating a client

The following command launches a step-by-step wizard to create a new client for
accessing a public register:

```sh
okdata pubreg create-client
```

Example values from the wizard:

![Example values from the wizard](img/pubreg-wizard.png)

## Listing clients

Use the following command to display a table of all of your clients:

```sh
okdata pubreg list-clients
```

## Deleting a client

When a client is no longer needed, it should be deleted by using the following
command:

```sh
okdata pubreg delete-client
```

Clients with active keys cannot be deleted. In such cases, their keys have to be
[deleted](#deleting-a-client-key) first.

Note that client deletion is irreversible.

## Creating a client key

Before creating client keys, you may want to grant a service user from the
dataplatform access to your AWS account's Parameter Store by following [these
steps](https://github.com/oslokommune/dataplattform/blob/master/origo/registerdata/offentlige-registerdata-3.md#%C3%A5pne-aws-konto). This
must be done if you want us to add and remove keys directly in your AWS
environment. It's also possible to generate keys locally and handle them
yourselves, if you prefer that.

The following command can be used to launch a step-by-step wizard to create a
new client key:

```sh
okdata pubreg create-key
```

Each client can hold a maximum of five keys. After reaching that limit, old keys
have to be [deleted](#deleting-a-client-key) to make room for new ones.

If you choose to store the client keys in Parameter Store, the following
parameters will be created:

- `/okdata/maskinporten/<client-id>/key.json`
  - A JSON object containing `key_alias`, `key_expiry`, `key_id`,
    `key_password`, and `keystore`.
- `/okdata/maskinporten/<client-id>/key_alias` (*deprecated*)
- `/okdata/maskinporten/<client-id>/key_id` (*deprecated*)
- `/okdata/maskinporten/<client-id>/key_password` (*deprecated*)
- `/okdata/maskinporten/<client-id>/keystore` (*deprecated*)

## Rotating a client key

Client keys expire 90 days after creation by default, but it's encouraged to
rotate them more often than that. When creating a new key and opting to send it
to your AWS account, you're also given the choice to activate automatic key
rotation for the client.

Automatic key rotation happens once every night Monday through Friday, replacing
the previous key in-place. That is, the old key is replaced in your AWS
account's Parameter Store with the new one. The previous key is still active for
five minutes after the switch before it is deleted, so your application can
assume that a key is valid for at least five minutes after fetching it from the
Parameter Store.

Keys that are subject to automatic rotation get a shorter expiration time of 7
days instead of 90 (though they should normally be rotated automatically before
that).

Automatic key rotation stops when the client is [deleted](#deleting-a-client).

### Rotating a client key manually

Client keys can also be rotated manually. To rotate a key manually, start by
[creating](#creating-a-client-key) a new key. If you opt to automatically send
it to your AWS account's Parameter Store, the newly generated key will replace
the old one in place (i.e. the old one will be overwritten). If you opt to
download the key locally, you'll have to replace the old key yourself.

After the new key has been installed, the old key can safely be
[deleted](#deleting-a-client-key).

## Listing client keys

Use the following command to display a table of all the keys registered on one
or all of your clients:

```sh
okdata pubreg list-keys
```

## Deleting a client key

When a key is no longer needed, it should be deleted by using the following
command:

```sh
okdata pubreg delete-key
```

Note that key deletion is irreversible.

## Viewing a client's audit log

To view the audit log for a client, use the following command:

```sh
okdata pubreg audit-log
```

Audit logs contain the history of events related to clients, including their
creation time, when keys are added and deleted, and the username of the user who
performed each action.

Note that audit logs for deleted clients can't be retrieved this way. Should
that become necessary, please contact Dataspeilet.
