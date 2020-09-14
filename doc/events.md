# Events

To see all operations available on events:
```bash
origo events -h
origo event_streams -h
```

Contents:
* [What is an event](#what-is-an-event)
* [Create event streams](#create-event-streams)
* [Event status](#event-status)
* [Delete event stream](#delete-event-stream)
* [Sending events](#sending-events)
* [Consuming events](#consuming-events)

## What is an event
Documentation is available on [GitHub](https://oslokommune.github.io/dataplattform/).

## Create event streams
An event stream is connected to a [dataset](datasets.md), and before you can continue with events you need to [create a dataset](datasets.md#create-dataset) and a [version](datasets.md#create-version) for that dataset. If this already exists you can continue with the following step to create an event stream:

```bash
origo event_streams create <datasetid> <versionid>
```

## Event status
A stream status must be `ACTIVE` before you can start sending events to it. To poll for the status manually:
```bash
origo event_streams ls <datasetid> <versionid>
```

Or you can check the value of status by passing the output to `jq`:
```bash
origo event_streams ls <datasetid> <versionid> --format=json | jq -r '.status'
```

## Delete event stream
Deleting an event stream can be done by executing:
```bash
origo event_streams delete <datasetid> <versionid>
```

## Sending events
After a stream has the status `ACTIVE` you can send events to it.

### Single JSON events
You can send events to your stream in different ways.

Single JSON events can be sent by piping a JSON string to the `events` command:
```bash
echo '{"hello": "world"}' | origo events put <datasetid> <versionid>
```

Given a file `event.json`:
```json
{
  "hello": "world"
}
```

you can either `cat` the contents of the file:
```bash
cat event.json | origo events put <datasetid> <versionid>
```

or reference it:

```bash
origo events put my-dataset 1 --file=/tmp/event.json
```

### Sending multiple json events
You can also send multiple events by piping them to the `events` command:
```bash
echo '[{"hello": "world"}, {"world": "hello"}]' | origo events put <datasetid> <versionid>
```

Given a file `events.json`:
```json
[
  {
    "hello": "world"
  },
  {
    "world": "hello"
  }
]
```
you can either cat the content of the file:

```bash
cat events.json | origo events put <datasetid> <versionid>
```

or reference it:

```bash
origo events put my-dataset 1 --file=events.json
```

## Consuming events
TBD
