import sys

from origocli.commands.datasets import DatasetsCommand


def test_command_get_cmd():
    args = ["datasets", "ls", "datasetid", "--format", "something"]
    old_sys_argv = sys.argv
    sys.argv = [old_sys_argv[0]] + args
    cmd = DatasetsCommand()

    assert cmd.cmd("ls") is True
    assert cmd.arg("datasetid") == "datasetid"
    assert cmd.opt("format") == "something"
    assert cmd.cmd("notexisting") is None
    assert cmd.arg("notexisting") is None
    assert cmd.opt("notexisting") is None

