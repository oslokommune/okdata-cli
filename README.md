# Oslo Origo CLI

Origo CLI provides a unified interface to the services provided by Oslo Origo

# Install
This is the first version of the Origo CLI, and should be treated as a alpha-version for now

Coming soon: ```pip install origocli```

Until then: see setup below for manual configuration of CLI

# Setup

Requirement: python 3.7

```
git clone git@github.com:oslokommune/origo-cli.git
cd origo-cli
python3 -m venv .venv
. .venv/bin/activate
make init
```

see [python documentation](doc/python.md) for installing python 3.7 on Ubuntu 1804 or Rasberry Pi

# Usage
Environment variables:

The cli will by default pick up configuration from current environment.
The credentials is resolved automatically if you do not set a specific Auth config, in the following order:

Note!

You do not need to set all four of: `ORIGO_USERNAME, ORIGO_PASSWORD, ORIGO_CLIENT_ID, ORIGO_CLIENT_SECRET`.
If you have been provided client_credentials then set: `ORIGO_CLIENT_ID, ORIGO_CLIENT_SECRET`. 
Otherwise set: `ORIGO_USERNAME, ORIGO_PASSWORD`
```
# keycloak user
export ORIGO_USERNAME=my-user

# keycloak password for ORIGO_USERNAME
export ORIGO_PASSWORD=my-password

# keycloak client
export ORIGO_CLIENT_ID=my-machine-client

# keycloak secret for ORIGO_CLIENT_ID
export ORIGO_CLIENT_SECRET=some-generated-secure-string


# overrides default environment (dev), but will be trumped by --env=<environment> on the commandline
export ORIGO_ENVIRONMENT=dev|prod

# If you are sending events and have been assigned a API key
export ORIGO_API_KEY=your-api-key
```
```
$ origo help
$ origo <command> help
```

## Commands available
* datasets
* events
* webhook_tokens
* help

## List all datasets
```
$ origo datasets ls
$ origo datasets ls my-dataset
$ origo datasets ls my-dataset my-edition
```

*Note*: For the correct, up to date, schema definition, please see [metadata-api schema catalogue](https://github.oslo.kommune.no/origo-dataplatform/metadata-api/tree/master/schema), the datasets below are for demonstration purposes

## Create dataset
File: dataset.json
```
{
    "title": "My dataset",
    "description": "My dataset description",
    "keywords": ["keyword", "for-indexing"],
    "accessRights": "public",
    "confidentiality": "green",
    "objective": "The objective for this dataset",
    "contactPoint": {
        "name": "Contact Name",
        "email": "contact.name@example.org",
        "phone": "999555111"
    },
    "publisher": "my organization",
    "processing_stage": "raw"
}

```
Create:
```
$ cat dataset.json | origo datasets create
```
This will create a dataset with ID=my-dataset, the id is derived from the title of the dataset. If another dataset exists with the same ID, a ID will be created with a random set of characters at the end of the id (eg: my-dataset-4nf7)

## Create version
File: version.json
```
{
  "version": "1"
}

```
Create:
```
$ cat version.json | origo datasets create-version my-dataset
```

## Create edition
File: edition.json
```
{
    "edition": "2019-01-01T12:00:00+01:01",
    "description": "My edition description",
    "startTime": "2019-01-01",
    "endTime": "2019-12-31"
}

```
Create:
```
$ cat edition.json | origo datasets create-edition my-dataset 1
```

## Upload file to edition
File: /tmp/test.txt
```
Hello, World!
```
Upload (will use latest edition on latest version if not specified with --version and --edition):
```
$ origo datasets cp /tmp/test.txt ds:my-dataset
```
The `cp` command operates with a `ds` prefix to specify

If an error occurs: ensure that the latest version have a edition

## Dataset access

Give user full access rights to a given dataset:

```
$ origo datasets create-access <datasetid> <userid>
```

Check if you have access to a given dataset:

```
$ origo datasets check-access <datasetid>
```


## Creating Event Streams

In order to create an event stream you will need to [create a dataset](#create-dataset) and [create a 
version](#create-version) for the dataset. If such already exist you are good to go.

Create:
```
$ origo event_streams create <datasetid> <version>
```
Note! You can not start sending event to the stream right away. You must wait until
the stream status is ACTIVE. To poll for the stream-status you can use the following (Get) `origo event_streams ls` - command.

Get:
```
$ origo event_streams ls <datasetid> <version>
```
Delete:
```
$ origo event_streams delete <datasetid> <version>
```

## Sending Events

In order to send events you need to [create an event stream](#creating-event-streams). 
If such already exist you are good to go.

Sending single json-events and lists of json-events can be done as follows:
```
$ echo '{"hello": "world"}' | origo events put <datasetid> <version>
$ echo '[{"hello": "world"}, {"world": "hello"}]' | origo events put <datasetid> <version>
$ cat /tmp/event.json | origo events put <datasetid> <version>
$ origo events put <datasetid> <version> --file=/tmp/event.json
```

## Webhook tokens

Create a new webhook token:

```
$ origo webhook_tokens create <datasetid> <service>
```

Delete (invalidate) specified webhook token:

```
$ origo webhook_tokens delete <datasetid> <token>
```