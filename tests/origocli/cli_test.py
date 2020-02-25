import sys
import io
import json
from requests.models import Response

import pytest
from bin.cli import get_command_class, main
from origo.exceptions import ApiAuthenticateError
from origo.sdk import SDK
from origocli.commands.datasets import DatasetsCommand
from origocli.command import generate_error_feedback


bad_request_response_body = {
    "message": "Validation error",
    "errors": ["wtf you trying to do?"],
}


def test_get_command_class():
    argv = ["origo", "datasets"]
    cmd = get_command_class(argv)
    assert cmd is DatasetsCommand


def test_main_http_error(raise_http_error):
    sys.argv = ["origo", "datasets", "create"]
    captured_output = io.StringIO()
    sys.stdout = captured_output
    main()
    expected_output = generate_error_feedback(
        bad_request_response_body["message"], bad_request_response_body["errors"]
    )
    assert captured_output.getvalue().strip("\n") == expected_output.strip("\n")


def test_main_auth_error(auth_failed):
    sys.argv = ["origo", "datasets", "create"]
    captured_output = io.StringIO()
    sys.stdout = captured_output
    main()
    assert captured_output.getvalue().strip("\n") == "Invalid credentials"


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
