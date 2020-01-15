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
pip install -e .
```

When developing towards the origo-sdk-python library:
```
cd origo-cli
python3 -m venv .venv
. .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:/Users/eide/Documents/workspace/oslokommune/origo-sdk-python/
python3 bin/cli.py datasets ls
```

# Tests
```
$ make test
```

# Usage
```
$ origo help
$ origo <command> help
```

## Commands available
* datasets
* events
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

## Using a pipeline
When you can upload a file to an edition, you can attach a Pipeline to the dataset.
The easiest way is by using the Pipeline Instance Wizard:
`origo pipelines intances wizard` 

### Wizard
1. Input a dataset id and select a version which the pipeline should write to
2. Select a pipeline
3. Input a transformation json object.
    3. A empty version of the transformation object is provided. All properties may not be required
4. Input a schema ID or leave it blank
5. Select whether or not the pipeline should create a new edition when completing a pipeline run.

When you upload a new data file, the pipeline will automatically start. 

### Manually
The requirements is a Pipeline Instance which refers to an existing Pipeline, and an output dataset. 
Lookup available Pipelines with `origo pipelines ls` 

pipeline_instance.json
```
{
    "pipelineArn": "arn:some:aws:id:to:123456789101:test-pipeline",
    "id": "my-dataset",
    "datasetUri": "output/my-dataset/1",
    "transformation": { "step1": "..." },
    "useLatestEdition": false
}
```
Pipeline Instance contains information about what to do in a pipeline. But a Pipeline Input is also required to indicate what will trigger the Instance.

Create by `origo pipelines instances create --file pipeline_instance.json`

pipeline_input.json
```
{
    "datasetUri": "input/my-dataset/1",
    "stage": "incoming",
    "pipelineInstanceId": "my-dataset"
}
```