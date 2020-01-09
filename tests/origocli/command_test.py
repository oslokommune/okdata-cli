import io
import sys

from origocli.command import BaseCommand
from origocli.output import TableOutput


def _set_argv(*args):
    old_sys_argv = sys.argv
    sys.argv = [old_sys_argv[0]] + list(args)


def test_docopt():
    _set_argv("datasets", "--debug", "--format", "yaml")

    cmd = BaseCommand()

    assert cmd.cmd("datasets") is True
    assert cmd.opt("debug") is True
    assert cmd.opt("format") == "yaml"
    assert cmd.cmd("notexisting") is None
    assert cmd.arg("notexisting") is None
    assert cmd.opt("notexisting") is None


def test_cmd_empty_handler():
    _set_argv("datasets", "--debug", "--format", "yaml")
    cmd = BaseCommand()
    assert cmd.handle() is None


def test_cmd_with_handler():
    _set_argv("datasets", "--debug", "--format", "yaml")
    cmd = BaseCommand()
    cmd.handler = lambda: True
    assert cmd.handle() is True


def test_cmd_with_sub_command():
    _set_argv("datasets", "--debug", "--format", "yaml")
    cmd = BaseCommand()
    sub_cmd = BaseCommand
    cmd.sub_commands = [sub_cmd]
    cmd.handler = lambda: True
    assert cmd.handle() is None


def test_invalid_docopt_for_subcommand():
    class SubCommand(BaseCommand):
        """
        usage:
            illegal usage
        """

    _set_argv("datasets", "--debug", "--format", "yaml")

    cmd = BaseCommand()
    cmd.sub_commands = [SubCommand]
    cmd.handler = lambda: True
    assert cmd.handle() is True


class FileCommand(BaseCommand):
    """
    usage:
        origo datasets -
        origo datasets --file=<file>
    """


def test_handle_input_from_file(mocker):
    mocker.patch("builtins.open", mocker.mock_open(read_data="open_file"))
    _set_argv("datasets", "--file", "input.json")
    cmd = FileCommand()
    content = cmd.handle_input()
    assert content == "open_file"


def test_handle_input_from_stdin(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("stdin"))
    _set_argv("datasets", "-")
    cmd = FileCommand()
    content = cmd.handle_input()
    assert content == "stdin"


def test_pretty_json(capsys):
    _set_argv("datasets")
    cmd = BaseCommand()
    cmd.pretty_json({"Hello": {"foo": "bar"}})
    captured = capsys.readouterr()
    assert (
        captured.out
        == '{\n  \x1b[94m"Hello"\x1b[39;49;00m: {\n    \x1b[94m"foo"\x1b[39;49;00m: \x1b[33m"bar"\x1b[39;49;00m\n  }\n}\n\n'
    )


def test_pretty_print_success(capsys):
    _set_argv("datasets")
    cmd = BaseCommand()
    config = {
        "name": {"name": "name", "key": "name"},
        "id": {"name": "key", "key": "key"},
    }
    cmd.print_success(TableOutput(config), [{"name": "hello", "key": "world"}])
    captured = capsys.readouterr()
    assert (
        captured.out
        == """+-------+-------+
|  name |  key  |
+-------+-------+
| hello | world |
+-------+-------+
"""
    )


def test_help(capsys):
    _set_argv("datasets")
    cmd = BaseCommand()
    cmd.help()
    captured = capsys.readouterr()
    assert captured.out == BaseCommand.__doc__
