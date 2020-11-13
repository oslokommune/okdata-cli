# Configuration

Contents:
* [Authentication](#authentication)
* [Environment](#environment)

## Authentication
All CRUD operations need an authenticated user in order to be executed. Some `ls` operations will not require a authenticated user, but might return a subset of available resources compared to that of a logged in user.

The user is loaded from the environment where `okdata` is executed.

### Oslo user
The CLI comes out of Oslo municipality, and any employee in Oslo will be able to use the CLI out of the box. The `OKDATA_USERNAME` maps to your Oslo user.

```bash
# Your Oslo user
export OKDATA_USERNAME=my-user

# Password for OKDATA_USERNAME
export OKDATA_PASSWORD=my-password
```

### Client user
For machine to machine communication and datasets related to large projects an Okdata client can be generated for you. Please contact us at [dataplattform@oslo.kommune.no](dataplattform@oslo.kommune.no) for setup.

```bash
# Okdata client
export OKDATA_CLIENT_ID=my-machine-client

# Secret for OKDATA_CLIENT_ID
export OKDATA_CLIENT_SECRET=some-generated-secure-string
```

Note: a client user should not be used as a shared user for convenience's sake!

### Order of loading user
The strategy of determining which user to choose is based on the following order:
1. `OKDATA_USERNAME`
2. `OKDATA_CLIENT_ID`

If both `OKDATA_USERNAME` and `OKDATA_CLIENT_ID` are in your `env` then `OKDATA_USERNAME` will be loaded and used for authentication.

### Debug/troubleshooting
If you have exported `OKDATA_USERNAME`, and then later `OKDATA_CLIENT_ID` to `env` you will still use `OKDATA_USERNAME` for authentication (and you think that you are using `OKDATA_CLIENT_ID`), please check this before reporting on any authentication problems.

Use `-d` at the end of your command and see the authentication strategy that has been chosen in the output.

The following output is shown when no user is found in `env`:
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

### Other users
Okdata is currently only supporting the two authentication mechanisms as described above, but we will support other authentication strategies like token-based authentication for the CLI in the future. Follow this document for changes.

We are also planning for a configuration-file (in `~/.okdata/credentials`) based authentication strategy with the possibility to choose between users and pass this as a parameter to the program: `okdata datasets ls --profile=my-dev-profile` or `export okdata_default_profile=my-dev-profile && okdata datasets ls`.

## Environment
`okdata` can be run in either `dev` or `prod`, depending on where you have your user and what you are doing.

When determining in which environment to run a command, the application loads the environment in the following order, and chooses the first it encounters:

1. `--env=prod|dev` option for every command
2. `OKDATA_ENVIRONMENT` from the current environment
3. Default: `prod`
