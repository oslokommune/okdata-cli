from bin.cli import get_command_class
from origocli.commands.datasets import DatasetsCommand


def test_get_command_class():
    argv = ["origo", "datasets"]
    cmd = get_command_class(argv)
    assert cmd is DatasetsCommand
