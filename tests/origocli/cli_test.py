import json
import sys

import pytest
from okdata.sdk import SDK
from okdata.sdk.exceptions import ApiAuthenticateError
from requests.models import Response

from okdata.cli.__main__ import get_command_class, main
from okdata.cli.command import _format_error_message
from okdata.cli.commands.datasets import DatasetsCommand


bad_request_response_body = {
    "message": "Validation error",
    "errors": ["wtf you trying to do?"],
}


def test_get_command_class():
    cmd = get_command_class(["okdata", "datasets"])
    assert cmd is DatasetsCommand

    cmd = get_command_class(["okdata", "datasets", "create"])
    assert cmd is DatasetsCommand

    cmd = get_command_class(["okdata", "datasets", "create", "--file=foo"])
    assert cmd is DatasetsCommand


def test_main_http_error(raise_http_error, capsys):
    sys.argv = ["okdata", "datasets", "create", "--file=foo"]
    main()
    expected_output = _format_error_message(
        bad_request_response_body["message"], bad_request_response_body["errors"]
    )
    assert capsys.readouterr().out.strip("\n") == expected_output.strip("\n")


def test_main_auth_error(auth_failed, capsys):
    sys.argv = ["okdata", "datasets", "create"]
    main()
    captured = capsys.readouterr().out.strip("\n")
    assert "An error occurred (ApiAuthenticateError)" in captured


@pytest.fixture()
def raise_http_error(monkeypatch):
    def bad_request(self):
        bad_request_response = Response()
        bad_request_response.status_code = 400
        bad_request_response._content = bytes(
            f"{json.dumps(bad_request_response_body)}", "utf-8"
        )
        bad_request_response.raise_for_status()

    monkeypatch.setattr(DatasetsCommand, "create_dataset", bad_request)


@pytest.fixture()
def auth_failed(monkeypatch):
    def auth_error(self):
        raise ApiAuthenticateError

    monkeypatch.setattr(SDK, "login", auth_error)
