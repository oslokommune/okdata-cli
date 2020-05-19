Events
=====
To see all operations available on events:
```
origo events -h
origo event_streams -h
```

TOC:
* [What is a event](#what-is-a-event)
* [Create event stream](#create-event-stream)
* [Event status](#event-status)
* [Delete event stream](#delete-event-stream)
* [Sending events](#sending-events)
* [Consuming events](#consuming-events)

# What is a event
Documentation is available on [github](https://oslokommune.github.io/dataplattform/)


# Create Event Streams
A event stream is connected to a [dataset](datasets.md), and before you can continue with events you need to [create a dataset](datasets.md#create-dataset) and a [version](datasets.md#create-version) for that dataset. If this already exist you can continue with the following steps:

Create:
```bash
origo event_streams create my-dataset 1
```

# Event status
A stream status must be ACTIVE before you can start sending events to it. To poll for the status manually:
```bash
origo event_streams ls my-dataset 1
```

Or you can check the value of status by passing the output to jq:
```bash
origo event_streams ls my-dataset 1 --format=json | jq -r '.status'
```

# Delete event stream
Deleting a event stream can be done by executing:
```bash
origo event_streams delete my-dataset 1
```

# Sending Events
After a stream have the status `ACTIVE` you can send events to it.

## Single json events
You can send events to your stream in different ways:

Sending json events by piping a single json event to the `events` command:
```bash
$ echo '{"hello": "world"}' | origo events put my-dataset 1
```

Given file event.json:
```json
{
  "hello": "world"
}
```
you can either cat the content of the file or reference it:
```bash
$ cat event.json | origo events put my-dataset 1
$ origo events put my-dataset 1 --file=/tmp/event.json
```

## Sending multiple json events
You can also send multiple events by piping them to the `events` command:
```bash
echo '[{"hello": "world"}, {"world": "hello"}]' | origo events put my-dataset 1
```

Given file events.json:
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
you can either cat the content of the file or reference it:

```bash
cat events.json | origo events put my-dataset 1
origo events put my-dataset 1 --file=events.json
```

# Consuming events
TBD
