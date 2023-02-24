import re
from operator import itemgetter

from questionary import Choice

from okdata.cli.commands.wizard import required_style

_providers = {
    "freg": "Folkeregisteret",
    "krr": "Kontaktregisteret",
    "skatt": "Skatteetaten",
}

_scopes = {
    "freg": [
        "folkeregister:deling/offentligmedhjemmel",
        "folkeregister:deling/offentligutenhjemmel",
    ],
    "krr": [
        "krr:global/digitalpost.read",
        "krr:global/kontaktinformasjon.read",
    ],
    "skatt": [
        "skatteetaten:arbeidsgiveravgift",
        "skatteetaten:avregning",
        "skatteetaten:boligsparingforungdom",
        "skatteetaten:inntekt",
        "skatteetaten:inntektsmottakere",
        "skatteetaten:mvameldingsopplysning",
        "skatteetaten:oppdragutenlandskevirksomheter",
        "skatteetaten:restanser",
        "skatteetaten:skattemelding",
        "skatteetaten:skatteplikt",
        "skatteetaten:spesifisertsummertskattegrunnlag",
        "skatteetaten:summertskattegrunnlag",
        "skatteetaten:tjenestepensjonsavtale",
    ],
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
        "message": "Maskinporten environment",
        "choices": _environments,
    }


def q_provider():
    return {
        **required_style,
        "type": "select",
        "name": "provider_id",
        "message": "Provider",
        "choices": [Choice(pname, pid) for pid, pname in _providers.items()],
    }


def q_scopes():
    return {
        **required_style,
        "type": "checkbox",
        "name": "scopes",
        "message": "Scopes",
        "choices": lambda x: _scopes[x["provider_id"]],
        "validate": (lambda choices: bool(choices) or "Select at least one scope"),
    }


def q_integration():
    def _validate_integration(text):
        if len(text) > 30:
            return "Too long!"
        if not re.fullmatch("[0-9a-z-]+", text):
            return 'Only lowercase letters, numbers and "-", please'
        return True

    return {
        **required_style,
        "type": "text",
        "name": "integration",
        "message": "Integration name",
        "instruction": (
            "(identifying in which system or case this client will be used)"
        ),
        "validate": _validate_integration,
    }


def q_client(pubreg_client, allow_all=False):
    def _client_choices(env):
        clients = pubreg_client.get_clients(env)

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
    }


def q_aws_account():
    return {
        **required_style,
        "type": "text",
        "name": "aws_account",
        "message": "AWS account number",
        "when": lambda x: x.get("key_destination") == "aws" or x.get("delete_from_aws"),
        "validate": (
            lambda t: bool(re.fullmatch("[0-9]{12}", t)) or "12 digits, please"
        ),
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


def q_key(pubreg_client):
    def _key_choices(env, client_id):
        keys = pubreg_client.get_keys(env, client_id)

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
