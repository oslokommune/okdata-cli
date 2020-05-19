Python
=====

TOC:
* [Installing python 3.7 on Ubuntu 1804](#installing-python-3-7-on-ubuntu-1804)

# Installing python 3.7 on Ubuntu 1804
Origio CLI requires python 3.6 to run, but if you have Ubuntu 1804, where 3.6 is installed by default you can upgrade to the latest 3.7 version if you choose to.

## Install from source
To install python 3.7 from source on ubuntu 1804 follow these steps. This will install buildtools, the required libraries and python-virtualenv to run origo CLI in
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
### Run CLI from compiled python
Once installed you can create a virtualenv for running origo CLI
```bash
git clone https://github.com/oslokommune/origo-cli.git
cd origo-cli
virtualenv -p /usr/local/bin/python3.7 venv37
source ./venv37/bin/activate
make init
origo datasets ls
```

## Install from apt
You can install python3.7 from deadsnakes ppa with the following steps:
```bash
sudo apt-add-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.7 python3.7-dev python-virtualenv python-dev build-essential
```
### Run CLI from installed python
Once installed you can create a virtualenv for running origo CLI
```bash
git clone https://github.com/oslokommune/origo-cli.git
cd origo-cli
virtualenv -p /usr/bin/python3.7 venv37
source ./venv37/bin/activate
make init
origo datasets ls
```
