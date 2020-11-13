# `okdata-cli` developer-documentation

## Setup

Requirement: Python 3.6+

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

## Tests
```bash
$ make test
```

## Documentation

Documentation is written in Markdown and is located in the `doc` directory. We
use Sphinx to compile it; run `make` inside the `doc` directory to see an
overview of all the available options.

An HTML version of the documentation is hosted at [Read the
Docs](https://okdata-cli.readthedocs.io/). This is kept up to date automatically
with the latest version on the `master` branch.

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
