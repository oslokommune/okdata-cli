# Datasets

To see all operations available on datasets:
```bash
origo datasets -h
```

Contents:
* [What is a dataset](#what-is-a-dataset)
* [List all datasets](#list-all-datasets)
* [Create dataset](#create-dataset)
  * [Parent dataset](#parent-dataset)
* [Create version](#create-version)
* [Create edition](#create-edition)
* [Upload file to edition](#upload-file-to-edition)
  * [Inspecting the upload status](#inspecting-the-upload-status)
* [Dataset access](#dataset-access)
* [Boilerplate](#boilerplate)

## What is a dataset
Documentation is available on [GitHub](https://oslokommune.github.io/dataplattform/).

## List all datasets
To explore datasets in Origo you can use the following commands:

```bash
origo datasets ls
origo datasets ls <datasetid>
origo datasets ls <datasetid> <versionid> <editionid>
```

To start exploring the datasets in Origo you do not need to log in, but based on the permissions set on each dataset you might get different lists.

*Note*: For the correct, up to date, schema definition, please see the [metadata-api schema catalogue](https://github.oslo.kommune.no/origo-dataplatform/metadata-api/tree/master/schema). The datasets below are for demonstration purposes.

To search for a specific dataset you can use the `--filter` option to search for only a subset of datasets available:

```bash
origo datasets ls --filter=<my-filter-string>
```

## Create dataset

File: `dataset.json`
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

Create the dataset by piping the contents of `dataset.json`:

```bash
cat dataset.json | origo datasets create
```

Or create it by referencing the file:

```bash
origo datasets create --file=dataset.json
```

This will create a dataset with ID `my-dataset`. The ID is derived from the title of the dataset. If another dataset exists with the same ID, an ID will be created with a random set of characters at the end of the ID (e.g. `my-dataset-4nf7`). There are no restrictions on dataset naming, but it is best practice to use your organization as the first part of the dataset title. For instance, `"title": "Origo developer portal statistics"` will generate a dataset with ID `origo-developer-portal-statistics`.

Write down the ID of the dataset. This must be used when creating versions, editions, or event streams.

### Parent dataset
If you have several datasets that are logically grouped together under a parent concept or idea, group them together by using the `parent_id` property of a dataset:

File: `dataset_with_parent.json`
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

## Create version
A version named "1" is created by default for new datasets. Unless you need to
create additional versions, you may safely skip the rest of this section.

File: `version.json`
```json
{
  "version": "2"
}
```

Create a new dataset version by piping the contents of `version.json`:

```bash
cat version.json | origo datasets create-version <datasetid>
```

Or create it by referencing the file:

```bash
origo datasets create-version <datasetid> --file=version.json
```

## Create edition
File: `edition.json`
```json
{
    "edition": "2019-01-01T12:00:00+01:01",
    "description": "My edition description",
    "startTime": "2019-01-01",
    "endTime": "2019-12-31"
}

```
Create the dataset version edition by piping the contents of `edition.json`:
```bash
cat edition.json | origo datasets create-edition <datasetid> <versionid>
```
Or create it by referencing the file:
```bash
origo datasets create-edition <datasetid> <versionid> --file=edition.json
```

## Upload file to edition
File: `/tmp/hello_world.csv`
```csv
hello, world
world, hello
```

Upload the file with the `cp` command to the `<datasetid>` dataset. Note the
`ds:` prefix for the target dataset.

To upload a file to a specific version and edition:
```bash
origo datasets cp /tmp/test.txt ds:<datasetid>/<versionid>/<editionid>
```

By using the special edition ID `latest`, the file will be uploaded to the
latest edition.

If no version or edition is provided, a new edition will be created for the
latest version automatically:

```bash
origo datasets cp /tmp/test.txt ds:<datasetid>
```

Or to upload to a new edition of a specific version:

```bash
origo datasets cp /tmp/test.txt ds:<datasetid>/<versionid>
```

### Inspecting the upload status

After uploading a file to a dataset using the `origo datasets cp` command, a
status ID is displayed which can be used to track the uploading process status:

```text
+-------------+---------------+---------------+------------+
| Dataset     | Local file    | Upload status | Status ID  |
+-------------+---------------+---------------+------------+
| <datasetid> | /tmp/test.txt | True          | <statusid> |
+-------------+---------------+---------------+------------+
```

To see the latest status of the upload, run:

```bash
origo status <statusid>
```

Or to see the complete status history of the uploading process:

```bash
origo status <statusid> --history
```

Passing `json` to the `--format` option displays the status in JSON format
instead, making the output more suitable for use in scripts. For instance to
continuously poll the upload status until it's finished:

```bash
######### Check status for the newly uploaded file #########
uploaded=false
echo "Checking status for uploaded file"
while ! $uploaded; do
  echo "\Checking upload status..."
  upload_status=`origo status $status_id --format=json`
  uploaded=`echo $upload_status | jq -r '.done'`
done
echo "Uploaded file is processed and ready to be consumed"
```

## Download file from dataset

The `origo datasets cp` command can also be used to download data form a dataset URI:

```bash
origo datasets cp ds:<datasetid>/<versionid>/<editionid> my/target/directory
```

If no version or edition is provided, the latest version and edition will be
used by default (if they exist):

```bash
origo datasets cp ds:<datasetid> my/target/directory
```

The target directory will be created if it doesn't already eixst on the local filesystem. The CLI also supports the use of `.` to specify the current working directory as output target.

## Dataset access

Give a user full access rights to a given dataset:
```bash
origo datasets create-access <datasetid> <userid>
```

Check if you current user/client have access to a given dataset:
```bash
origo datasets check-access <datasetid>
```

## Boilerplate
The process of setting up a full dataset, version, edition with a properly configured pipeline that will process your data involves a few steps. A boilerplate command is provided for you to create a full set of files and configurations that will set everything up, all you have to do is to update a few files with the correct information, and you will be up and running in no time.

Currently there are two pipelines available: `csv-to-parquet` and `data-copy`, but we are working on more, and if you have been given a custom pipeline from Origo you can still use the boilerplate functionality, you just need to update the `pipeline.json` file generated with one you will get from us.

* `data-copy`: a pipeline that does not alter the original input data, useful for Excel files, documents, or any other file that your dataset contains
* `csv-to-parquet`: generate [Parquet](https://en.wikipedia.org/wiki/Apache_Parquet) files from CSV input files

To create a set of files run the following command. It will create a directory in the current working directory called `my-dataset`:
```bash
origo datasets boilerplate my-dataset
```
The boilerplate command will give a input prompt to gather all necessary information needed in order to generate a dataset with corresponding pipeline.

When running the command (see output of the boilerplate command) a default file will be uploaded to test the pipeline. To override this add a `--file=<file>`:
```bash
origo datasets boilerplate my-dataset --file=/tmp/file_to_upload.csv
```

If you don't need, or want to customize the files before running the supplied script, you can skip the prompt, but you then need to supply one of the pipelines available:
```bash
origo datasets boilerplate my-dataset --pipeline=data-copy --prompt=no
```

The output of the command will notify you on which files you will need to update before running the supplied `run.sh` command.

### Best practice
In order to keep your datasets and processing pipelines structured it is recommended that you create a directory structure with the following layout:
```
- my-organization-datasets
  - my-organization-statistics
  - my-organization-insight
  - my-organization-events
```
and commit this to your source repository (git or other). This will also help in debugging or troubleshooting any issues that might arise, and will make it easy to deploy to production after testing.

Any output from the `run.sh` command or manually executed command should also be piped to a logfile in order to look up the IDs created and be a part of the troubleshooting if need be.
