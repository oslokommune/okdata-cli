# Install

## Requirements
Origo CLI requires the following to run:

* Python 3.6 or higher
* `make` and build tools for installing Python modules; see output from `make init` below to see any other requirements you must install in order to install Origo CLI

In addition it is recommended to use a tool like `jq` to parse and make automated decisions based on output.

## Installation with pip
The quickest way to get started is by installing the latest release of Origo CLI from PyPI with pip:

```bash
pip install origo-cli
```

## Installation from source
If you have git installed and would like to update incrementally from source, you can clone the Origo CLI repository from GitHub:

```bash
git clone https://github.com/oslokommune/origo-cli.git
```

If you don't have git installed you can download the source from GitHub with one of the following:

* From [Origo CLI's GitHub page](https://github.com/oslokommune/origo-cli) choose `Code ▾` and then `Download ZIP`
* From a terminal: `curl -LO https://github.com/oslokommune/origo-cli/archive/master.zip`

Unzip the downloaded file and rename the unzipped directory to `origo-cli` to follow the rest of the installation process.

### Setup
Installing Origo CLI into a virtual environment is recommended:

```bash
cd origo-cli
python -m venv .venv
source .venv/bin/activate
make init
```

This will install all dependencies and enable a new command in the venv: `origo`. To verify that it is installed properly and working, try listing all datasets:

```bash
origo datasets ls
```

Installing and running the program will create a `~/.origo` directory where settings and caches will be stored.

## Upgrade
If you have installed Origo CLI with pip:

```bash
pip install --upgrade origo-cli
```

If you have checked out the source from GitHub:

```bash
git pull
pip install -r requirements.txt
```

If you download the source code in zip format, redownload it and redo the steps [Setup](#setup).

## Uninstall
If you have installed Origo CLI with pip:

```bash
pip uninstall origo-cli
```

Otherwise simply remove the `origo-cli` directory.

To remove all traces of the program, remove the ` ~/.origo` directory as well.
