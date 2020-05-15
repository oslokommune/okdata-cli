# Oslo Origo CLI Developer-documentation

## Setup

Requirement: Python 3.6+

Setup:
```
git clone git@github.com:oslokommune/origo-cli.git
cd origo-cli
python3 -m venv .venv
. .venv/bin/activate
make init
```

When developing towards the origo-sdk-python library:
```
cd origo-cli
python3 -m venv .venv
. .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:/<path-to-sdk>/origo-sdk-python/
python3 bin/cli.py datasets ls
```

## Tests
```
$ make test
```
