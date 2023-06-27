# `okdata-cli` developer-documentation

## Setup

Requirement: Python 3.8+

Setup:
```bash
git clone git@github.com:oslokommune/okdata-cli.git
cd okdata-cli
python3 -m venv .venv
source .venv/bin/activate
make init
```

When developing towards the okdata-sdk library:
```bash
cd okdata-cli
python3 -m venv .venv
. .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:/<path-to-sdk>/okdata-sdk-python/
python3 bin/cli.py datasets ls
```

## Environment

`okdata` can be run in either `dev` or `prod`.

When determining in which environment to run a command, the application loads
the environment in the following order, and chooses the first it encounters:

1. `--env=prod|dev` option for every command
2. `OKDATA_ENVIRONMENT` from the current environment
3. Default: `prod`

## Tests

```bash
$ make test
```

## Documentation

Documentation is written in Markdown and is located in the `doc` directory.

## Uploading to PyPI

Okdata CLI releases are hosted at [PyPI](https://pypi.org/project/okdata-cli/),
making it easy to install using `pip install okdata-cli`.

Use the following recipe when uploading a new release to PyPI:

```bash
python3 setup.py sdist bdist_wheel
twine upload dist/*
```

This depends on having the packages `setuptools`, `wheel`, and `twine`
installed.
