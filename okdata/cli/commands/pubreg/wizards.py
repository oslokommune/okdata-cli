import re

from prompt_toolkit.styles import Style
from questionary import Choice, prompt

required_style = Style([("qmark", "fg:red bold")])


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


class CreateClientWizard:
    """Wizard for the `pubreg create-client` command."""

    def __init__(self, teams):
        self.teams = teams

    def _team_choices(self):
        return [Choice(t["name"], t["id"]) for t in self.teams]

    def _validate_integration(self, text):
        if len(text) > 30:
            return "Too long!"
        if not re.fullmatch("[0-9a-z-]+", text):
            return 'Only lowercase letters, numbers and "-", please'
        return True

    def start(self):
        choices = prompt(
            [
                {
                    "type": "select",
                    "qmark": "*",
                    "style": required_style,
                    "name": "env",
                    "message": "Environment",
                    "choices": _environments,
                },
                {
                    "type": "select",
                    "qmark": "*",
                    "style": required_style,
                    "name": "team_id",
                    "message": "Team",
                    "choices": lambda x: self._team_choices(),
                },
                {
                    "type": "select",
                    "qmark": "*",
                    "style": required_style,
                    "name": "provider_id",
                    "message": "Provider",
                    "choices": [
                        Choice(pname, pid) for pid, pname in _providers.items()
                    ],
                },
                {
                    "type": "checkbox",
                    "qmark": "*",
                    "style": required_style,
                    "name": "scopes",
                    "message": "Scopes",
                    "choices": lambda x: _scopes[x["provider_id"]],
                    "validate": (
                        lambda choices: bool(choices) or "Select at least one scope"
                    ),
                },
                {
                    "type": "text",
                    "qmark": "*",
                    "style": required_style,
                    "name": "integration",
                    "message": "Component/integration name",
                    "validate": self._validate_integration,
                },
            ]
        )

        return {
            "env": choices["env"],
            "team_id": choices.get("team_id"),
            "provider_id": choices["provider_id"],
            "provider_name": _providers[choices["provider_id"]],
            "integration": choices["integration"],
            "scopes": choices["scopes"],
        }


class CreateKeyWizard:
    """Wizard for the `pubreg create-key` command."""

    def __init__(self, client):
        self.client = client

    def _client_choices(self, env):
        clients = self.client.get_clients(env)

        if not clients:
            raise NoClientsError

        return [
            Choice(
                c["client_name"],
                {"id": c["client_id"], "name": c["client_name"]},
            )
            for c in clients
        ]

    def start(self):
        choices = prompt(
            [
                {
                    "type": "select",
                    "qmark": "*",
                    "style": required_style,
                    "name": "env",
                    "message": "Environment",
                    "choices": _environments,
                },
                {
                    "type": "select",
                    "qmark": "*",
                    "style": required_style,
                    "name": "client",
                    "message": "Client",
                    "choices": lambda x: self._client_choices(x["env"]),
                },
                {
                    "type": "confirm",
                    "qmark": "*",
                    "style": required_style,
                    "name": "send_to_aws",
                    "message": "Send key to AWS Parameter Store?",
                    "auto_enter": False,
                },
                {
                    "type": "text",
                    "qmark": "*",
                    "style": required_style,
                    "name": "aws_account",
                    "message": "AWS account number",
                    "when": lambda x: x["send_to_aws"],
                    "validate": (
                        lambda t: bool(re.fullmatch("[0-9]{12}", t))
                        or "12 digits, please"
                    ),
                },
                {
                    "type": "select",
                    "qmark": "*",
                    "style": required_style,
                    "name": "aws_region",
                    "message": "AWS region",
                    "when": lambda x: x["send_to_aws"],
                    "choices": [Choice(*r) for r in _aws_regions],
                },
            ]
        )

        return {
            "env": choices["env"],
            "client_id": choices["client"]["id"],
            "client_name": choices["client"]["name"],
            "aws_account": choices.get("aws_account"),
            "aws_region": choices.get("aws_region"),
        }
