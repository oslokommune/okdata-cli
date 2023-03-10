# Configuration

Most `okdata` commands require you to be authenticated. Though some operations
(like `okdata datasets ls`) doesn't require you to be authenticated, they might
return only a subset of available resources compared to that of a logged in
user.

## Oslo kommune user

Employees in Oslo kommune can authenticate with Okdata CLI by setting the
following two environment variables:

```bash
# Your Oslo kommune username (e.g. ooo123456)
export OKDATA_USERNAME=$(op read op://Private/ooo/username)

# Password for OKDATA_USERNAME
export OKDATA_PASSWORD=$(op read op://Private/ooo/password)
```

The username and password are retrieved from 1Password in these examples.

## Client user

For machine to machine communication, an Okdata client can be generated for
you. Please contact us at
[dataplattform@oslo.kommune.no](dataplattform@oslo.kommune.no) if you need one.

```bash
# Okdata client
export OKDATA_CLIENT_ID=$(op read op://Shared/my-client/id)

# Secret for OKDATA_CLIENT_ID
export OKDATA_CLIENT_SECRET=$(op read op://Shared/my-client/secret)
```

Note: a client user should not be used as a shared user for convenience's sake!

## User loading order

The strategy of determining which user to choose is based on the following order:

1. `OKDATA_USERNAME`
2. `OKDATA_CLIENT_ID`

If both `OKDATA_USERNAME` and `OKDATA_CLIENT_ID` are in your environment then
`OKDATA_USERNAME` will be loaded and used for authentication.

## Debug/troubleshooting

Use `-d` at the end of your command and see the authentication strategy that has
been chosen in the output.

The following output is shown when no user is found in the environment:

```text
INFO:root:Could not resolve value for OKDATA_CLIENT_ID
INFO:root:Could not resolve value for OKDATA_CLIENT_SECRET
INFO:root:Could not resolve value for OKDATA_USERNAME
INFO:root:Could not resolve value for OKDATA_PASSWORD
INFO:root:Initializing auth object
INFO:root:No valid auth strategies available
```

When `OKDATA_USERNAME` is used:

```text
INFO:root:Initializing auth object
INFO:root:Found credentials for TokenServiceProvider
```

When `OKDATA_CLIENT_ID` is used:

```text
INFO:root:Initializing auth object
INFO:root:Found credentials for ClientCredentialsProvider
```
