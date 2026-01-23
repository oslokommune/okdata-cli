import io

import pytest

from conftest import set_argv
from okdata.cli.command import BaseCommand, _format_error_message
from okdata.cli.output import TableOutput


def test_docopt():
    set_argv("datasets", "--debug", "--format", "yaml")

    cmd = BaseCommand()

    assert cmd.cmd("datasets") is True
    assert cmd.opt("debug") is True
    assert cmd.opt("format") == "yaml"
    assert cmd.cmd("notexisting") is None
    assert cmd.arg("notexisting") is None
    assert cmd.opt("notexisting") is None


def test_cmd_empty_handler():
    set_argv("datasets", "--debug", "--format", "yaml")
    with pytest.raises(NotImplementedError):
        BaseCommand().handle()


def test_cmd_with_handler():
    set_argv("datasets", "--debug", "--format", "yaml")
    cmd = BaseCommand()
    cmd.handler = lambda: True
    assert cmd.handle() is True


def test_cmd_with_sub_command():
    set_argv("datasets", "--debug", "--format", "yaml")
    cmd = BaseCommand()
    sub_cmd = BaseCommand
    cmd.sub_commands = [sub_cmd]
    cmd.handler = lambda: True

    with pytest.raises(NotImplementedError):
        cmd.handle()


def test_invalid_docopt_for_subcommand():
    class SubCommand(BaseCommand):
        """
        usage:
            illegal usage
        """

    set_argv("datasets", "--debug", "--format", "yaml")

    cmd = BaseCommand()
    cmd.sub_commands = [SubCommand]
    cmd.handler = lambda: True
    assert cmd.handle() is True


class FileCommand(BaseCommand):
    """
    usage:
        okdata datasets -
        okdata datasets --file=<file>
    """


def test_handle_input_from_file(mocker):
    mocker.patch("builtins.open", mocker.mock_open(read_data="open_file"))
    set_argv("datasets", "--file", "input.json")
    cmd = FileCommand()
    content = cmd.handle_input()
    assert content == "open_file"


def test_handle_input_from_stdin(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("stdin"))
    set_argv("datasets", "-")
    cmd = FileCommand()
    content = cmd.handle_input()
    assert content == "stdin"


def test_pretty_json(capsys):
    set_argv("datasets")
    cmd = BaseCommand()
    cmd.pretty_json({"Hello": {"foo": "bar"}})
    captured = capsys.readouterr()
    assert captured.out == """{
  "Hello": {
    "foo": "bar"
  }
}
"""


def test_pretty_print_success(capsys):
    set_argv("datasets")
    cmd = BaseCommand()
    config = {
        "name": {"name": "name", "key": "name"},
        "id": {"name": "key", "key": "key"},
    }
    cmd.print_success(TableOutput(config), [{"name": "hello", "key": "world"}])
    captured = capsys.readouterr()
    assert captured.out == """+-------+-------+
| name  | key   |
+-------+-------+
| hello | world |
+-------+-------+
"""


def test_pretty_print_fields_single(capsys):
    set_argv("datasets")
    cmd = BaseCommand()
    config = {
        "name": {"name": "name", "key": "name"},
        "id": {"name": "key", "key": "key", "fields": ["a"]},
    }
    cmd.print_success(TableOutput(config), [{"name": "hello", "key": {"a": "world"}}])
    captured = capsys.readouterr()
    assert captured.out == """+-------+-------+
| name  | key   |
+-------+-------+
| hello | world |
+-------+-------+
"""


def test_pretty_print_fields_multiple(capsys):
    set_argv("datasets")
    cmd = BaseCommand()
    config = {
        "name": {"name": "name", "key": "name"},
        "id": {"name": "key", "key": "key", "fields": ["a", "b"]},
    }
    cmd.print_success(
        TableOutput(config), [{"name": "hello", "key": {"a": "world", "b": "world"}}]
    )
    captured = capsys.readouterr()
    assert captured.out == """+-------+-------+
| name  | key   |
+-------+-------+
| hello | world |
|       | world |
+-------+-------+
"""


def test_pretty_print_wrapped_success(capsys):
    set_argv("datasets")
    cmd = BaseCommand()
    config = {
        "name": {"name": "name", "key": "name"},
        "id": {"name": "key", "key": "key", "wrap": 15},
    }
    cmd.print_success(
        TableOutput(config),
        [{"name": "wrap", "key": "some long text that needs wrapping"}],
    )
    captured = capsys.readouterr()
    assert captured.out == """+------+----------------+
| name | key            |
+------+----------------+
| wrap | some long text |
|      | that needs     |
|      | wrapping       |
+------+----------------+
"""


def test_pretty_print_multiple_wrapped_success(capsys):
    set_argv("datasets")
    cmd = BaseCommand()
    config = {
        "name": {"name": "name", "key": "name"},
        "id": {"name": "key", "key": "key", "wrap": 15},
    }
    cmd.print_success(
        TableOutput(config),
        [
            {
                "name": "wrap",
                "key": ["some longer text that needs wrapping", "even more text here"],
            }
        ],
    )
    captured = capsys.readouterr()
    assert captured.out == """+------+-------------------+
| name | key               |
+------+-------------------+
| wrap | - some longer     |
|      |   text that needs |
|      |   wrapping        |
|      | - even more text  |
|      |   here            |
+------+-------------------+
"""


def test_help(capsys):
    set_argv("datasets")
    cmd = BaseCommand()
    cmd.help()
    captured = capsys.readouterr()
    assert captured.out == BaseCommand.__doc__


def test_format_error_message():
    assert _format_error_message("foo") == "An error occurred: foo"
    assert (
        _format_error_message("foo", "bar") == "An error occurred: foo\nCause:\n - bar"
    )
    assert (
        _format_error_message("foo", ["bar"])
        == "An error occurred: foo\nCause:\n - bar"
    )
    assert (
        _format_error_message("foo", ["bar", "baz"])
        == "An error occurred: foo\nCauses:\n - bar\n - baz"
    )
    assert (
        _format_error_message("foo", [{"msg": "bar"}])
        == "An error occurred: foo\nCause:\n - bar"
    )
    assert (
        _format_error_message("foo", [{"msg": "bar"}, {"msg": "baz"}])
        == "An error occurred: foo\nCauses:\n - bar\n - baz"
    )
