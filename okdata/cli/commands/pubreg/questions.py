import re
from operator import itemgetter

from prompt_toolkit.styles import Style
from questionary import Choice

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


class NoTeamError(Exception):
    pass


_common_style = {
    "qmark": "*",
    "style": Style([("qmark", "fg:red bold")]),
}


def q_env():
    return {
        **_common_style,
        "type": "select",
        "name": "env",
        "message": "Maskinporten environment",
        "choices": _environments,
    }


def q_team(team_client):
    def _team_choices():
        teams = team_client.get_teams(has_role="origo-team")

        if not teams:
            raise NoTeamError

        return [Choice(t["name"], t["id"]) for t in teams]

    return {
        **_common_style,
        "type": "select",
        "name": "team_id",
        "message": "Team",
        "choices": _team_choices(),
    }


def q_provider():
    return {
        **_common_style,
        "type": "select",
        "name": "provider_id",
        "message": "Provider",
        "choices": [Choice(pname, pid) for pid, pname in _providers.items()],
    }


def q_scopes():
    return {
        **_common_style,
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
        **_common_style,
        "type": "text",
        "name": "integration",
        "message": "Integration name",
        "instruction": (
            "(identifying in which system or case this client will be used)"
        ),
        "validate": _validate_integration,
    }


def q_client(pubreg_client):
    def _client_choices(env):
        clients = pubreg_client.get_clients(env)

        if not clients:
            raise NoClientsError

        return [
            Choice(
                c["client_name"],
                {"id": c["client_id"], "name": c["client_name"]},
            )
            for c in sorted(clients, key=itemgetter("client_name"))
        ]

    return {
        **_common_style,
        "type": "select",
        "name": "client",
        "message": "Client",
        "choices": lambda x: _client_choices(x["env"]),
    }


def q_key_destination():
    return {
        **_common_style,
        "type": "select",
        "name": "key_destination",
        "message": "Where should the key be stored?",
        "choices": [
            Choice("Send the key to your AWS Parameter Store", "aws"),
            Choice("Save the key locally", "local"),
        ],
    }


def q_aws_account():
    return {
        **_common_style,
        "type": "text",
        "name": "aws_account",
        "message": "AWS account number",
        "when": lambda x: x["key_destination"] == "aws",
        "validate": (
            lambda t: bool(re.fullmatch("[0-9]{12}", t)) or "12 digits, please"
        ),
    }


def q_aws_region():
    return {
        **_common_style,
        "type": "select",
        "name": "aws_region",
        "message": "AWS region",
        "when": lambda x: x["key_destination"] == "aws",
        "choices": [Choice(*r) for r in _aws_regions],
    }


def q_key(pubreg_client):
    def _key_choices(env, client_id):
        keys = pubreg_client.get_keys(env, client_id)

        if not keys:
            raise NoKeysError

        return sorted([k["kid"] for k in keys])

    return {
        **_common_style,
        "type": "select",
        "name": "key_id",
        "message": "Key",
        "choices": lambda x: _key_choices(x["env"], x["client"]["id"]),
    }
