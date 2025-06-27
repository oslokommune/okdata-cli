# Install

The quickest way to get started is by installing the latest release of Okdata
CLI from [PyPI](https://pypi.org/project/okdata-cli) with pip (requires Python
3.9 or higher):

```bash
python -m pip install --user okdata-cli
```

Alternatively by using [pipx](https://pipx.pypa.io):

```bash
pipx install okdata-cli
```

This will make the `okdata` command available to you. To verify that it is
installed properly and working, try listing all datasets:

```bash
okdata datasets ls
```

If this succeeds you're ready to proceed with [configuration](configuration.md)!

## Alternative installation from source

Alternatively, Okdata CLI can be installed directly from source if you would
like to track updates before they appear in a proper PyPI release.

Start by cloning the [Okdata CLI
repository](https://github.com/oslokommune/okdata-cli) from GitHub:

```bash
git clone https://github.com/oslokommune/okdata-cli.git
```

Proceed by installing Okdata CLI into a virtual environment:

```bash
cd okdata-cli
python -m venv .venv
source .venv/bin/activate
make init
```

This will install all necessary dependencies and make the `okdata` command
available inside the virtual environment.

Installation from source is also possible with pipx:

```bash
pipx install 'git+https://github.com/oslokommune/okdata-cli.git#egg=okdata-cli'
```

## Upgrade

If you have installed Okdata CLI with pip:

```bash
python -m pip install --user --upgrade okdata-cli
```

If you have installed Okdata CLI with pipx:

```bash
pipx upgrade okdata-cli
```

Or if you have checked out the source from GitHub:

```bash
git pull
pip install -r requirements.txt
```

## Uninstall

If you have installed Okdata CLI with pip:

```bash
python -m pip uninstall okdata-cli
```

If you have installed Okdata CLI with pipx:

```bash
pipx uninstall okdata-cli
```

Otherwise simply remove the `okdata-cli` source directory.

To remove all traces of the program, remove the ` ~/.okdata` directory as well.
