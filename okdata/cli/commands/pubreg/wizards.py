import re

from prompt_toolkit.styles import Style
from questionary import Choice, prompt

required_style = Style([("qmark", "fg:red bold")])

_teams = [
    ("Automatiserte prosesser", "automatiserte-prosesser"),
    ("Booking", "booking"),
    ("Dataplattform", "dataplattform"),
    ("Dataspeilet", "dataspeilet"),
    ("Informasjonsflyt", "informasjonsflyt"),
    ("Kjøremiljø og verktøy", "kjoremiljo"),
    ("Legevaktmottak", "legevaktmottak"),
    ("Min Side", "min-side"),
    ("Oslonøkkelen", "oslonokkelen"),
    ("Proaktive meldinger", "proaktive-meldinger"),
    ("Skjema", "skjema"),
    ("Veiviser", "veiviser"),
]

_providers = [
    ("Folkeregisteret", "freg"),
    ("Kontaktregisteret", "krr"),
    ("Skatteetaten", "skatt"),
]

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


class ClientCreateWizard:
    """Wizard for the `pubreg create-client` command."""

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
                    "name": "team",
                    "message": "Team",
                    "choices": [Choice(*t) for t in _teams],
                },
                {
                    "type": "select",
                    "qmark": "*",
                    "style": required_style,
                    "name": "provider",
                    "message": "Provider",
                    "choices": [Choice(*p) for p in _providers],
                },
                {
                    "type": "text",
                    "qmark": "*",
                    "style": required_style,
                    "name": "integration",
                    "message": "Component/integration name",
                    "validate": self._validate_integration,
                },
                {
                    "type": "checkbox",
                    "qmark": "*",
                    "style": required_style,
                    "name": "scopes",
                    "message": "Scopes",
                    "choices": lambda x: _scopes[x["provider"]],
                    "validate": (
                        lambda choices: bool(choices) or "Select at least one scope"
                    ),
                },
                {
                    "type": "select",
                    "qmark": "*",
                    "style": required_style,
                    "name": "environment",
                    "message": "Environment",
                    "choices": ["test", "prod"],
                },
            ]
        )

        return {
            "provider": choices["provider"],
            "integration": choices["integration"],
            "scopes": choices["scopes"],
            "environment": choices["environment"],
            "team": choices.get("team"),
        }
