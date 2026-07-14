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
* [Dataset access](#dataset-access)

## What is a dataset
Documentation is available on [GitHub](https://oslokommune.github.io/dataplattform/).

## List all datasets
To explore datasets in Okdata you can use the following commands:

```bash
okdata datasets ls
okdata datasets ls <dataset_id>
okdata datasets ls <dataset_id>/<version>
okdata datasets ls <dataset_id>/<version>/<edition>
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
cat version.json | okdata datasets create-version <dataset_id>
```

Or create it by referencing the file:

```bash
okdata datasets create-version <dataset_id> --file=version.json
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
cat edition.json | okdata datasets create-edition <dataset_id> <version>
```
Or create it by referencing the file:
```bash
okdata datasets create-edition <dataset_id> <version> --file=edition.json
```

## Dataset access

See [permissions](permissions.md).
