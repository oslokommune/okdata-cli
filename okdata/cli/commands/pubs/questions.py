from operator import attrgetter, itemgetter

from questionary import Choice

from okdata.cli.commands.validators import (
    AWSAccountValidator,
    IntegrationValidator,
    URIListValidator,
    URIValidator,
)
from okdata.cli.commands.wizard import filter_comma_separated, required_style

client_types = {
    "idporten": "ID-porten",
    "maskinporten": "Maskinporten",
}

_environments = [
    "test",
    "prod",
]

_aws_regions = [
    ("eu-central-1 (Frankfurt)", "eu-central-1"),
    ("eu-north-1 (Stockholm)", "eu-north-1"),
    ("eu-west-1 (Ireland)", "eu-west-1"),
]


class NoClientsError(Exception):
    pass


class NoKeysError(Exception):
    pass


def q_env():
    return {
        **required_style,
        "type": "select",
        "name": "env",
        "message": "Environment",
        "choices": _environments,
    }


def q_client_type():
    return {
        **required_style,
        "type": "select",
        "name": "client_type_id",
        "message": "Client type",
        "choices": [Choice(pname, pid) for pid, pname in client_types.items()],
    }


def q_provider(providers):
    return {
        **required_style,
        "type": "select",
        "name": "provider_id",
        "message": "Provider",
        "choices": sorted(
            [Choice(pname, pid) for pid, pname in providers.items()],
            key=attrgetter("title"),
        ),
        "when": lambda x: x.get("client_type_id") == "maskinporten",
    }


def q_scopes(scopes):
    return {
        **required_style,
        "type": "checkbox",
        "name": "scopes",
        "message": "Scopes",
        "choices": lambda x: (
            sorted(scopes[x["provider_id"]]) if "provider_id" in x else []
        ),
        "validate": (lambda choices: bool(choices) or "Select at least one scope"),
        "when": lambda x: x.get("client_type_id") == "maskinporten",
    }


def q_integration():
    return {
        **required_style,
        "type": "text",
        "name": "integration",
        "message": "Integration name",
        "instruction": (
            "(identifying in which system or case this client will be used)"
        ),
        "validate": IntegrationValidator,
    }


def q_redirect_uris():
    return {
        **required_style,
        "type": "text",
        "name": "redirect_uris",
        "message": "Redirect URIs (comma-separated)",
        "filter": filter_comma_separated,
        "when": lambda x: x.get("client_type_id") == "idporten",
        "validate": URIListValidator,
    }


def q_post_logout_redirect_uris():
    return {
        **required_style,
        "type": "text",
        "name": "post_logout_redirect_uris",
        "message": "Post logout Redirect URIs (comma-separated)",
        "filter": filter_comma_separated,
        "when": lambda x: x.get("client_type_id") == "idporten",
        "validate": URIListValidator,
    }


def q_frontchannel_logout_uri():
    return {
        **required_style,
        "type": "text",
        "name": "frontchannel_logout_uri",
        "message": "Frontchannel logout URI",
        "when": lambda x: x.get("client_type_id") == "idporten",
        "validate": URIValidator,
    }


def q_client_uri():
    return {
        **required_style,
        "type": "text",
        "name": "client_uri",
        "message": "Client URI (back URI)",
        "when": lambda x: x.get("client_type_id") == "idporten",
        "validate": URIValidator,
    }


def q_client(pubs_client, allow_all=False):
    def _client_choices(env):
        clients = pubs_client.get_clients(env)

        if not clients:
            raise NoClientsError

        sorted_clients = sorted(clients, key=itemgetter("client_name"))

        def client(c):
            return {"id": c["client_id"], "name": c["client_name"]}

        return [Choice(c["client_name"], client(c)) for c in sorted_clients] + (
            [Choice("All clients", [client(c) for c in sorted_clients])]
            if allow_all
            else []
        )

    return {
        **required_style,
        "type": "select",
        "name": "client",
        "message": "Client",
        "choices": lambda x: _client_choices(x["env"]),
    }


def q_key_destination():
    return {
        **required_style,
        "type": "select",
        "name": "key_destination",
        "message": "Where should the key be stored?",
        "choices": [
            Choice("Send the key to your AWS Parameter Store", "aws"),
            Choice("Save the key locally", "local"),
        ],
    }


def q_delete_from_aws():
    return {
        **required_style,
        "type": "confirm",
        "name": "delete_from_aws",
        "message": "Delete key from AWS Parameter Store?",
        "auto_enter": False,
        "default": False,
    }


def q_aws_account():
    return {
        **required_style,
        "type": "text",
        "name": "aws_account",
        "message": "AWS account number",
        "when": lambda x: x.get("key_destination") == "aws" or x.get("delete_from_aws"),
        "validate": AWSAccountValidator,
    }


def q_aws_region():
    return {
        **required_style,
        "type": "select",
        "name": "aws_region",
        "message": "AWS region",
        "when": lambda x: x.get("key_destination") == "aws" or x.get("delete_from_aws"),
        "choices": [Choice(*r) for r in _aws_regions],
    }


def q_enable_auto_rotate():
    return {
        **required_style,
        "type": "confirm",
        "name": "enable_auto_rotate",
        "message": "\n".join(
            [
                "Automatic key rotation will replace the key in SSM nightly on weekdays.",
                "  Enable automatic key rotation for this client?",
            ]
        ),
        "when": lambda x: x.get("key_destination") == "aws",
        "auto_enter": False,
    }


def q_key(pubs_client):
    def _key_choices(env, client_id):
        keys = pubs_client.get_keys(env, client_id)

        if not keys:
            raise NoKeysError

        return sorted([k["kid"] for k in keys])

    return {
        **required_style,
        "type": "select",
        "name": "key_id",
        "message": "Key",
        "choices": lambda x: _key_choices(x["env"], x["client"]["id"]),
    }
