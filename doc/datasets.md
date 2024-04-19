# Datasets

To see all operations available on datasets:
```bash
okdata datasets -h
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

## What is a dataset
Documentation is available on [GitHub](https://oslokommune.github.io/dataplattform/).

## List all datasets
To explore datasets in Okdata you can use the following commands:

```bash
okdata datasets ls
okdata datasets ls <datasetid>
okdata datasets ls <datasetid> <versionid> <editionid>
```

To start exploring the datasets in Okdata you do not need to log in, but based on the permissions set on each dataset you might get different lists.

*Note*: For the correct, up to date, schema definition, please see the [metadata-api schema catalogue](https://github.oslo.kommune.no/origo-dataplatform/metadata-api/tree/master/schema). The datasets below are for demonstration purposes.

To search for a specific dataset you can use the `--filter` option to search for only a subset of datasets available:

```bash
okdata datasets ls --filter=<my-filter-string>
```

## Create dataset

Enter `okdata datasets create` to start the dataset creation wizard. After
answering a number of questions, a new dataset is created along with a selected
processing pipeline, ready to receive files.

### From a configuration file

Datasets can also be created from a configuration file if you need more fine
grained control (this will not set up a pipeline). This method is also suitable
if you need to script the dataset creation flow.

File: `dataset.json`
```json
{
    "title": "My dataset",
    "description": "My dataset description",
    "keywords": ["keyword", "for-indexing"],
    "accessRights": "public",
    "objective": "The objective for this dataset",
    "contactPoint": {
        "name": "Contact Name",
        "email": "contact.name@example.org"
    },
    "publisher": "my organization"
}
```

Create the dataset by referencing the file:

```bash
okdata datasets create --file=dataset.json
```

This will create a dataset with ID `my-dataset`. The ID is derived from the title of the dataset. If another dataset exists with the same ID, an ID will be created with a random set of characters at the end of the ID (e.g. `my-dataset-4nf7`). There are no restrictions on dataset naming, but it is best practice to use your organization as the first part of the dataset title. For instance, `"title": "Origo developer portal statistics"` will generate a dataset with ID `origo-developer-portal-statistics`.

Write down the ID of the dataset. This must be used when creating versions and editions.

### Parent dataset
If you have several datasets that are logically grouped together under a parent concept or idea, group them together by using the `parent_id` property of a dataset:

File: `dataset_with_parent.json`
```json
{
    "title": "Origo statistics developer portal",
    "description": "My dataset description",
    "keywords": ["keyword", "for-indexing"],
    "accessRights": "public",
    "objective": "The objective for this dataset",
    "contactPoint": {
        "name": "Contact Name",
        "email": "contact.name@example.org"
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
cat version.json | okdata datasets create-version <datasetid>
```

Or create it by referencing the file:

```bash
okdata datasets create-version <datasetid> --file=version.json
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
cat edition.json | okdata datasets create-edition <datasetid> <versionid>
```
Or create it by referencing the file:
```bash
okdata datasets create-edition <datasetid> <versionid> --file=edition.json
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
okdata datasets cp /tmp/test.txt ds:<datasetid>/<versionid>/<editionid>
```

By using the special edition ID `latest`, the file will be uploaded to the
latest edition.

If no version or edition is provided, a new edition will be created for the
latest version automatically:

```bash
okdata datasets cp /tmp/test.txt ds:<datasetid>
```

Or to upload to a new edition of a specific version:

```bash
okdata datasets cp /tmp/test.txt ds:<datasetid>/<versionid>
```

### Inspecting the upload status

After uploading a file to a dataset using the `okdata datasets cp` command, a
trace ID is displayed which can be used to track the uploading process status:

```text
+-------------+---------------+-----------+-------------+
| Dataset     | Local file    | Uploaded? | Trace ID    |
+-------------+---------------+-----------+-------------+
| <datasetid> | /tmp/test.txt | Yes       | <trace_id>  |
+-------------+---------------+-----------+-------------+
```

To see the latest status of the upload, run:

```bash
okdata status <trace_id>
```

Or to see the complete status history of the uploading process:

```bash
okdata status <trace_id> --history
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
  upload_status=`okdaata status $trace_id --format=json`
  uploaded=`echo $upload_status | jq -r '.done'`
done
echo "Uploaded file is processed and ready to be consumed"
```

## Download file from dataset

The `okdata datasets cp` command can also be used to download data form a dataset URI:

```bash
okdata datasets cp ds:<datasetid>/<versionid>/<editionid> my/target/directory
```

If no version or edition is provided, the latest version and edition will be
used by default (if they exist):

```bash
okdata datasets cp ds:<datasetid> my/target/directory
```

The target directory will be created if it doesn't already eixst on the local filesystem. The CLI also supports the use of `.` to specify the current working directory as output target.

## Dataset access

See [permissions](permissions.md).
