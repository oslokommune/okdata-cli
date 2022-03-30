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
* [Creating a client key](#creating-a-client-key)
* [Listing client keys](#listing-client-keys)

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

Examples values from the wizard:

![Examples values from the wizard](img/pubreg-wizard.png)

## Listing clients

Use the following command to display a table of all of your clients:

```sh
okdata pubreg list-clients <maskinporten-env>
```

## Creating a client key

Before creating client keys, you'll need to grant a service user from the
dataplatform access to your AWS account's Parameter Store by following [these
steps](https://github.com/oslokommune/dataplattform/blob/master/origo/registerdata/offentlige-registerdata-3.md#%C3%A5pne-aws-konto).
This is done in order to allow us to inject the generated keys directly into
your AWS environment.

When that's in place, the following command can be used to create new keys:

```sh
okdata pubreg create-key <maskinporten-env> <client-id> <aws-account> <aws-region>
```

## Listing client keys

Use the following command to display a table of all the keys registered on one
of your clients:

```sh
okdata pubreg list-keys <maskinporten-env> <client-id>
```
