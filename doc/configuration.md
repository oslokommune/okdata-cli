# Configuration

Contents:
* [Authentication](#authentication)
* [Environment](#environment)

## Authentication
All CRUD operations need an authenticated user in order to be executed. Some `ls` operations will not require a authenticated user, but might return a subset of available resources compared to that of a logged in user.

The user is loaded from the environment where `origo` is executed.

### Oslo user
The CLI comes out of Oslo municipality, and any employee in Oslo will be able to use the CLI out of the box. The `ORIGO_USERNAME` maps to your Oslo user.

```bash
# Your Oslo user
export ORIGO_USERNAME=my-user

# Password for ORIGO_USERNAME
export ORIGO_PASSWORD=my-password
```

### Client user
For machine to machine communication and datasets related to large projects an Origo client can be generated for you. Please contact us at [dataplattform@oslo.kommune.no](dataplattform@oslo.kommune.no) for setup.

```bash
# Origo client
export ORIGO_CLIENT_ID=my-machine-client

# Secret for ORIGO_CLIENT_ID
export ORIGO_CLIENT_SECRET=some-generated-secure-string
```

Note: a client user should not be used as a shared user for convenience's sake!

### Order of loading user
The strategy of determining which user to choose is based on the following order:
1. `ORIGO_USERNAME`
2. `ORIGO_CLIENT_ID`

If both `ORIGO_USERNAME` and `ORIGO_CLIENT_ID` are in your `env` then `ORIGO_USERNAME` will be loaded and used for authentication.

### Debug/troubleshooting
If you have exported `ORIGO_USERNAME`, and then later `ORIGO_CLIENT_ID` to `env` you will still use `ORIGO_USERNAME` for authentication (and you think that you are using `ORIGO_CLIENT_ID`), please check this before reporting on any authentication problems.

Use `-d` at the end of your command and see the authentication strategy that has been chosen in the output.

The following output is shown when no user is found in `env`:
```text
INFO:root:Could not resolve value for ORIGO_CLIENT_ID
INFO:root:Could not resolve value for ORIGO_CLIENT_SECRET
INFO:root:Could not resolve value for ORIGO_USERNAME
INFO:root:Could not resolve value for ORIGO_PASSWORD
INFO:root:Initializing auth object
INFO:root:No valid auth strategies available
```

When `ORIGO_USERNAME` is used:
```text
INFO:root:Initializing auth object
INFO:root:Found credentials for TokenServiceProvider
```

When `ORIGO_CLIENT_ID` is used:
```text
INFO:root:Initializing auth object
INFO:root:Found credentials for ClientCredentialsProvider
```

### Other users
Origo is currently only supporting the two authentication mechanisms as described above, but we will support other authentication strategies like token-based authentication for the CLI in the future. Follow this document for changes.

We are also planning for a configuration-file (in `~/.origo/credentials`) based authentication strategy with the possibility to choose between users and pass this as a parameter to the program: `origo datasets ls --profile=my-dev-profile` or `export origo_default_profile=my-dev-profile && origo datasets ls`.

## Environment
`origo` can be run in either `dev` or `prod`, depending on where you have your user and what you are doing.

When determining in which environment to run a command, the application loads the environment in the following order, and chooses the first it encounters:

1. `--env=prod|dev` option for every command
2. `ORIGO_ENVIRONMENT` from the current environment
3. Default: `prod`
