# Events

To see all operations available on events:
```bash
origo events -h
```

Contents:
* [What is an event](#what-is-an-event)
* [Create event streams](#create-event-streams)
* [Event status](#event-status)
* [Delete event stream](#delete-event-stream)
* [Sending events](#sending-events)
  * [Single json events](#single-json-events)
  * [Sending multiple json events](#sending-multiple-json-events)
* [Sinks](#sinks)
* [Subscribable event streams](#subscribable-event-streams)

## What is an event
Documentation is available on [GitHub](https://oslokommune.github.io/dataplattform/).

## Create event streams
An event stream is connected to a [dataset](datasets.md), and before you can continue with events you need to [create a dataset](datasets.md#create-dataset) and a [version](datasets.md#create-version) for that dataset. If this already exists you can continue with the following step to create an event stream:

```bash
origo events create-stream <dataset-uri>
```

# Event status
A stream status must be `ACTIVE` before you can start [sending events](#sending-events) to it. To poll for the streams status manually:
```bash
origo events describe-stream <dataset-uri>
```

Or you can check the value of status by passing the output to `jq`:
```bash
origo events describe-stream <dataset-uri> --format=json | jq -r '.stream.status'
```

## Delete event stream
Deleting an event stream can be done by executing:
```bash
origo events delete-stream <dataset-uri>
```

## Sending events
After a stream has the status `ACTIVE` you can send events to it.

### Single JSON events
You can send events to your stream in different ways.

Single JSON events can be sent by piping a JSON string to the `events` command:
```bash
echo '{"hello": "world"}' | origo events put <dataset-uri>
```

Given a file `event.json`:
```json
{
  "hello": "world"
}
```

you can either `cat` the contents of the file:
```bash
cat event.json | origo events put <dataset-uri>
```

or reference it:

```bash
origo events put ds:my-dataset/1 --file=/tmp/event.json
```

### Sending multiple json events
You can also send multiple events by piping them to the `events` command:
```bash
echo '[{"hello": "world"}, {"world": "hello"}]' | origo events put <dataset-uri>
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
cat events.json | origo events put <dataset-uri>
```

or reference it:

```bash
origo events put ds:my-dataset/1 --file=events.json
```

# Sinks

Event stream sinks (`s3` or `elasticsearch`) can be enabled by using the following command:

```bash
origo events enable-sink <datasetid> <versionid> --sink-type=<sink_type>
```

The status of these resources can be polled using `describe-stream`:

```bash
origo events describe-stream <dataset-uri>
```

To disable a given sink, use the following command:

```bash
origo events disable-sink <dataset-uri> --sink-type=<sink_type>
```


# Subscribable event streams

It is possible to "subscribe" to an event stream using the WebSocket protocol. This feature can be enabled/disabled on demand:

```bash
origo events enable-subscription <dataset-uri>
origo events disable-subscription <dataset-uri>
```
