# Python

Contents:
* [Installing Python 3.7 on Ubuntu 18.04](#installing-python-3-7-on-ubuntu-18-04)

## Installing Python 3.7 on Ubuntu 18.04
Okdata CLI requires at least Python 3.7 to run, but if you have Ubuntu 18.04, where 3.6 is installed by default, you can upgrade to the latest 3.7 version if you choose to.

### Install from source
To install Python 3.7 from source on Ubuntu 18.04 follow these steps. This will install buildtools, the required libraries and python-virtualenv to run Okdata CLI in.
```bash
sudo apt update
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget python-virtualenv
wget https://www.python.org/ftp/python/3.7.6/Python-3.7.6.tgz
tar -xf Python-3.7.6.tgz
cd Python-3.7.6
# Run configure with '--enable-optimizations' to optimize the build, but this will take a while
./configure
make -j 8
sudo make altinstall
python3.7 --version
```
#### Run CLI from compiled Python
Once installed you can create a virtualenv for running Okdata CLI.
```bash
git clone https://github.com/oslokommune/okdata-cli.git
cd okdata-cli
virtualenv -p /usr/local/bin/python3.7 venv37
source ./venv37/bin/activate
make init
okdata datasets ls
```

### Install from apt
You can install Python 3.7 from deadsnakes ppa with the following steps:
```bash
sudo apt-add-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.7 python3.7-dev python-virtualenv python-dev build-essential
```
#### Run CLI from installed Python
Once installed you can create a virtualenv for running Okdata CLI.
```bash
git clone https://github.com/oslokommune/okdata-cli.git
cd okdata-cli
virtualenv -p /usr/bin/python3.7 venv37
source ./venv37/bin/activate
make init
okdata datasets ls
```
