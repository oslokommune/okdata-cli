Install
=====

# Requirements
Origo CLI requires the following to run:
* `python 3.6`
* `make` and build tools for installing python modules, see output from `make init` below to see any other requirements you must install in order to install Origo CLI

In addition it is recommended to use a tool like `jq` to parse and make automated decisions based on output.

# Install
Origo CLI is not yet installable as a application via pip (coming soon), but must be downloaded from github in order to be set up

## Git clone
If you have git installed and would like to update incremental from source you can install Origo CLI from github:
```bash
git clone https://github.com/oslokommune/origo-cli.git
```

## Download zip
If you don't have git installed: download the source from github with one of the following:

* From https://github.com/oslokommune/origo-cli choose `clone or download` and choose `Download ZIP`
* From a terminal: `curl -LO https://github.com/oslokommune/origo-cli/archive/master.zip`

Unzip source the downloaded file and move to `origo-cli` to follow the rest of the install process

## Install
Installing Origo CLI into a virtual environment is recommended:
```bash
cd origo-cli
python -m venv .venv
source .venv/bin/activate
make init
```

This will install all dependencies and enable a new command in the venv: `origo`. To verify that it is installed properly and working, try listing all datasets: `origo datasets ls`

Installing and running the program will create a `~/.origo` folder where settings and caches will be stored

# Upgrade
If you have checked out the source from github: `git pull`, then `pip install -r requirement.txt`

If you download the source code in zip format: run the install script again in the newly downloaded folder.

# Delete
To remove all traces of the program remove this folder and run `rm -rf ~/.origo`
