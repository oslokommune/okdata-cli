Datasets
=====
To see all operations available on datasets:
```bash
origo datasets -h
```

TOC:
* [What is a dataset](#what-is-a-dataset)
* [List datasets](#list-all-dataset)
* [Create datasets](#create-dataset)
  * [Parent dataset](#parent-dataset)
* [Create version](#create-version)
* [Create edition](#create-edition)
* [Upload file to edition](#upload-file-to-edition)
* [Dataset access](#dataset-access)
* [Boilerplate](#boilerplate)


# What is a dataset
Documentation is available on [github](https://oslokommune.github.io/dataplattform/)


# List all datasets
To explore datasets in Origo you can use the following commands:
```bash
origo datasets ls
origo datasets ls <datasetid>
origo datasets ls <datasetid> <versionid> <editionid>
```
To start exploring the datasets in Origo you do not need to log in, but: based on the permissions set on each dataset you might get different lists

*Note*: For the correct, up to date, schema definition, please see [metadata-api schema catalogue](https://github.oslo.kommune.no/origo-dataplatform/metadata-api/tree/master/schema), the datasets below are for demonstration purposes

To search for a specific dataset you can use the `--filter` option to search for only a subset of datasets available
```bash
origo datasets ls --filter=<my-filter-string>
```

# Create dataset

File: dataset.json
```json
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
    "publisher": "my organization"
}

```

Create the dataset by piping the contents of dataset.json:
```bash
cat dataset.json | origo datasets create
```

Or create it by referencing the file:
```bash
origo datasets create --file=dataset.json
```

This will create a dataset with id=`my-dataset`. The id is derived from the title of the dataset. If another dataset exists with the same ID, a ID will be created with a random set of characters at the end of the id (eg: `my-dataset-4nf7`). There are no prefix or restrictions on dataset naming, but it is best practice to use your organization as the first part of your dataset title: `"title": "Origo developer portal statistics"`  that will generate a dataset with `id=origo-developer-portal-statistics`

Write down the id of the dataset, this must be used when creating version, editions or event streams.

## Parent dataset
If you have several datasets that are logically grouped together under a parent concept or idea: group them together by using the `parent_id` property of a dataset:

File: dataset_with_parent.json
```json
{
    "title": "Origo statistics developer portal",
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
    "parent_id": "origo-statistics"
}
```
This will logically group all statistics together, and you can set permissions on the `parent_id` to grant access to all child datasets.

# Create version
File: version.json
```json
{
  "version": "1"
}

```
Create the dataset version by piping the contents of version.json:
```bash
cat version.json | origo datasets create-version <datasetid>
```
Or create it by referencing the file:
```bash
origo datasets create-version <datasetid> --file=version.json
```

# Create edition
File: edition.json
```
{
    "edition": "2019-01-01T12:00:00+01:01",
    "description": "My edition description",
    "startTime": "2019-01-01",
    "endTime": "2019-12-31"
}

```
Create the dataset version edition by piping the contents of edition.json:
```bash
cat edition.json | origo datasets create-edition <datasetid> <versionid>
```
Or create it by referencing the file:
```bash
origo datasets create-edition <datasetid> <versionid> --file=edition.json
```

# Upload file to edition
File: /tmp/hello_world.csv
```csv
hello, world
world, hello
```

Upload the file with the `cp` command to the `<datasetid>` dataset. Note the `ds`-prefix for upload command, this specifies to upload to a specific dataset.
When `version` or `edition` are not specified it will result in auto-discovery of the latest edition on the latest version
```bash
origo datasets cp /tmp/test.txt ds:<datasetid>
```

To upload a file to a specific version and edition:
```bash
origo datasets cp /tmp/test.txt ds:<datasetid> <versionid> <editionid>
```

The `cp` command also supports a `ds://` prefix to specify a dataset uri e.g `ds://my-dataset/my-version/my-edition`.

# Download file from dataset

The `$ origo datasets cp` can also be used to download data form a dataset uri.
```
$ origo datasets cp ds://my-dataset/my-version/my-edition my/target/directory
```
If no version or edition is provided, then the CLI will by default choose the latest version and edition (if these exist).

If the target directory does not exist on local machine, the CLI will create the directory. The cli also supports the use of `.` to
specify working directory as output path.

# Dataset access

Give a user full access rights to a given dataset:
```bash
origo datasets create-access <datasetid> <userid>
```

Check if you current user/client have access to a given dataset:
```bash
origo datasets check-access <datasetid>
```

# Boilerplate
The process of setting up a full dataset, version, edition with a properly configured pipeline that will process your data involves a few steps. A boilerplate command is provided for you to create a full set of files and configurations that will set everything up, all you have to do is to update a few files with the correct information, and you will be up and running in no time.

Currently there is only a single pipeline available: `csv-to-parquet`, but we are working on more, and if you have been given a custom pipeline from Origo you can still use the boilerplate functionality, you just need to update the pipeline.json file generated with one you will get from us.

To create a set of files run the following command, this will create a folder in the current working directory called `my-dataset`:
```bash
origo datasets boilerplate csv-to-parquet my-dataset
```

The output of the command will notify you on which files you will need to update before running the supplied `run.sh` command
## Best practice
In order to keep your datasets and processing pipelines structured it is recommended that you create a directory structure with the following layout:
```
- my-organization-datasets
  - my-organization-statistics
  - my-organization-insight
  - my-organization-events
```
and commit this to your source repository (git or other). This will also help in debugging or troubleshooting any issues that might arise (and will make it easy to deploy to production after testing)

Any output from the `run.sh` command or manually executed command should also be piped to a logfile in order to look up the IDs created and be a part of the troubleshooting if need be.
