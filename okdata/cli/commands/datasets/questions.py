from questionary import Choice

from okdata.cli.commands.validators import (
    KeywordValidator,
    SimpleEmailValidator,
    TitleValidator,
)
from okdata.cli.commands.wizard import filter_comma_separated, required_style

pipeline_choices = {
    "file": [
        Choice("Lagre dataen slik den er", "data-copy"),
        Choice("Konverter fra CSV til Delta", "csv-to-delta"),
        Choice("Konverter fra JSON til Delta", "json-to-delta"),
        Choice("Konverter fra CSV til Parquet", "csv-to-parquet"),
        Choice("Konverter fra Excel til CSV", "pipeline-excel-to-csv"),
        Choice("Ingen prosessering (krever manuell konfigurasjon av pipeline)", False),
    ],
}

available_pipelines = [
    choice.value
    for category in pipeline_choices.values()
    for choice in category
    if choice.value
]


def qs_create_dataset():
    return [
        {
            **required_style,
            "type": "select",
            "name": "sourceType",
            "message": "Datakilde",
            "choices": [
                Choice("Fil", "file"),
                Choice("Punktmålinger", "event"),
                Choice("Ingen (datasettet skal ikke inneholde data direkte)", "none"),
            ],
        },
        {
            **required_style,
            "type": "text",
            "name": "title",
            "message": "Tittel",
            "validate": TitleValidator,
        },
        {"type": "text", "name": "description", "message": "Beskrivelse"},
        {"type": "text", "name": "objective", "message": "Formål"},
        {
            **required_style,
            "type": "text",
            "name": "keywords",
            "message": "Nøkkelord (komma-separert)",
            "validate": KeywordValidator,
            "filter": filter_comma_separated,
        },
        {
            **required_style,
            "type": "select",
            "name": "accessRights",
            "message": "Tilgangsnivå",
            "choices": [
                Choice("Eksplisitt tilgangskontroll", "non-public"),
                Choice("Internt til Origo", "restricted"),
                Choice("Offentlig", "public"),
            ],
        },
        {
            **required_style,
            "type": "select",
            "name": "license",
            "message": "Lisens",
            "choices": [
                Choice("Uspesifisert (ingen gjenbruk)", ""),
                Choice(
                    "Norsk lisens for offentlige data (NLOD) – siste gjeldende versjon",
                    "http://data.norge.no/nlod/",
                ),
                Choice(
                    "Norsk lisens for offentlige data (NLOD) 2.0",
                    "http://data.norge.no/nlod/no/2.0/",
                ),
                Choice(
                    "Norsk lisens for offentlige data (NLOD) 1.0",
                    "http://data.norge.no/nlod/no/1.0/",
                ),
                Choice(
                    "Creative Commons – Navngivelse 4.0 Internasjonal (CC BY 4.0)",
                    "http://creativecommons.org/licenses/by/4.0/",
                ),
                Choice(
                    "Creative Commons – Fristatus-erklæring (CC0 1.0 Universal)",
                    "http://creativecommons.org/publicdomain/zero/1.0/",
                ),
            ],
        },
        {"type": "text", "name": "name", "message": "Kontaktperson – navn"},
        {
            **required_style,
            "type": "text",
            "name": "email",
            "message": "Kontaktperson – epost",
            "validate": SimpleEmailValidator,
        },
        {"type": "text", "name": "publisher", "message": "Utgiver"},
        {
            **required_style,
            "type": "select",
            "name": "pipeline",
            "message": "Prosessering",
            "choices": lambda x: pipeline_choices.get(x["sourceType"]),
            "when": lambda x: x["sourceType"] in pipeline_choices,
        },
    ]


def qs_create_pipeline():
    return [
        {
            **required_style,
            "type": "select",
            "name": "pipeline",
            "message": "Prosessering",
            "choices": pipeline_choices["file"],
        },
    ]
