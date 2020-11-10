import sys

import pytest
from okdata.cli.command import BaseCommand

BASECMD_QUAL = f"{BaseCommand.__module__}.{BaseCommand.__name__}"


def set_argv(*args):
    old_sys_argv = sys.argv
    sys.argv = [old_sys_argv[0]] + list(args)


@pytest.fixture
def mock_print_success(mocker):
    return mocker.patch(f"{BASECMD_QUAL}.print_success")


@pytest.fixture
def mock_print(mocker):
    return mocker.patch(f"{BASECMD_QUAL}.print")


@pytest.fixture
def mock_pretty_json(mocker):
    return mocker.patch(f"{BASECMD_QUAL}.pretty_json")
