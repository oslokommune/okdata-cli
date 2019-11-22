from origocli.command import Command


def test_command_get_cmd():
    args = {}
    args["ls"] = True
    args["<datasetid>"] = True
    args["--format"] = True
    cmd = Command(args)

    assert cmd.cmd("ls") is True
    assert cmd.arg("datasetid") is True
    assert cmd.opt("format") is True
    assert cmd.cmd("notexisting") is None
    assert cmd.arg("notexisting") is None
    assert cmd.opt("notexisting") is None
