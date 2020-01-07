import sys

from bin.cli import main


def test_command_get_cmd():
    args = {}
    args["ls"] = True
    args["<datasetid>"] = True
    args["--format"] = True
    old_sys_argv = sys.argv
    sys.argv = [old_sys_argv[0]] + args
    cmd = main()

    assert cmd.cmd("ls") is True
    assert cmd.arg("datasetid") is True
    assert cmd.opt("format") is True
    assert cmd.cmd("notexisting") is None
    assert cmd.arg("notexisting") is None
    assert cmd.opt("notexisting") is None

