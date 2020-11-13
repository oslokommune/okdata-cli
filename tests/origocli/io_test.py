import io
import os
import pathlib
import tempfile

from okdata.cli.io import read_json


def test_read_json_from_file():
    with tempfile.NamedTemporaryFile() as f:
        f.write(b'{"foo": "bar"}')
        f.seek(0)

        assert read_json(f.name) == {"foo": "bar"}


def test_read_json_from_homedir():
    with tempfile.NamedTemporaryFile(dir=pathlib.Path.home()) as f:
        f.write(b'{"foo": "bar"}')
        f.seek(0)

        filename = "~/{}".format(os.path.basename(f.name))

        assert read_json(filename) == {"foo": "bar"}


def test_read_json_from_stdin(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO('{"foo": "bar"}'))

    assert read_json() == {"foo": "bar"}
