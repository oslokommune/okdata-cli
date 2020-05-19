Webhooks
=====
To see all operations available for webhooks:
```
origo webhooks -h
```

TOC:
* [What is a webhook](#what-is-a-webhook)
* [Create token](#create-token)
* [Delete token](#delete-token)


# What is webhook
Documentation is available on [github](https://oslokommune.github.io/dataplattform/)

# Create token

Create a new webhook token:

```bash
origo webhooks create-token <datasetid> <service>
```

# Delete token
Delete (invalidate) specified webhook token:

```bash
origo webhooks delete-token <datasetid> <token>
```
