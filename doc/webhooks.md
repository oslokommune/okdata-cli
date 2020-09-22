# Webhooks

To see all operations available for webhooks:
```bash
origo webhooks -h
```

Contents:
* [What is a webhook](#what-is-a-webhook)
* [Create token](#create-token)
* [Delete token](#delete-token)


## What is a webhook
Documentation is available on [GitHub](https://oslokommune.github.io/dataplattform/).

## Create token

Create a new webhook token:

```bash
origo webhooks create-token <datasetid> <service>
```


## List tokens

Lists all active webhook tokens for a dataset:

```bash
origo webhooks list-tokens <datasetid>
```

## Delete token
Delete (invalidate) specified webhook token:

```bash
origo webhooks delete-token <datasetid> <token>
```
