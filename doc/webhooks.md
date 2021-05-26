# Webhooks

To see all operations available for webhooks:

```bash
okdata webhooks -h
```

Contents:
* [What is a webhook](#what-is-a-webhook)
* [Create token](#create-token)
* [Delete token](#delete-token)
* [List tokens](#list-tokens)

## What is a webhook

Documentation is available on
[our website](https://oslokommune.github.io/dataplattform/om-data/begreper).

## Create token

To create a new webhook token:

```bash
okdata webhooks create-token <datasetid> <operation>
```

Currently supported operations are `read` and `write`, creating a token with
read- or write access to the dataset `datasetid`, respectively.

## Delete token

To delete (invalidate) a specified webhook token for a dataset:

```bash
okdata webhooks delete-token <datasetid> <token>
```

## List tokens

To list all active webhook tokens for a dataset:

```bash
okdata webhooks list-tokens <datasetid>
```
