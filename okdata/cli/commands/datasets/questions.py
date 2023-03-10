import csv

from questionary import Choice

from okdata.cli.commands.datasets.validators import (
    KeywordValidator,
    PhoneValidator,
    SimpleEmailValidator,
    SpatialResolutionValidator,
    SpatialValidator,
    StandardsValidator,
    TitleValidator,
)
from okdata.cli.commands.wizard import required_style

pipeline_choices = {
    "file": [
        Choice("Lagre dataen slik den er", "data-copy"),
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


def filter_comma_separated(value):
    values = next(
        csv.reader([value], delimiter=",", escapechar="\\", skipinitialspace=True)
    )
    return [x.strip() for x in values if x]


def qs_create(include_extra_metadata=True):
    return [
        {
            **required_style,
            "type": "select",
            "name": "sourceType",
            "message": "Datakilde",
            "choices": [
                Choice("Fil", "file"),
                Choice("Database (krever eget databaseoppsett)", "database"),
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
            "type": "confirm",
            "name": "contains_geodata",
            "message": "Inneholder datasettet geodata?",
            "default": False,
            "when": lambda x: include_extra_metadata,
        },
        {
            "type": "text",
            "name": "spatial",
            "message": "Romlig avgrensning (komma-separert)",
            "validate": SpatialValidator,
            "filter": filter_comma_separated,
            "when": lambda x: include_extra_metadata and x["contains_geodata"],
        },
        {
            "type": "text",
            "name": "spatialResolutionInMeters",
            "message": "Romlig oppløsning (i meter)",
            "validate": SpatialResolutionValidator,
            "filter": lambda v: float(v.replace(",", ".")) if v else None,
            "when": lambda x: include_extra_metadata and x["contains_geodata"],
        },
        {
            "type": "text",
            "name": "conformsTo",
            "message": "I samsvar med standarder (komma-separert)",
            "validate": StandardsValidator,
            "filter": filter_comma_separated,
            "when": lambda x: include_extra_metadata,
        },
        {
            **required_style,
            "type": "select",
            "name": "accessRights",
            "message": "Tilgangsnivå",
            "choices": [
                Choice("Offentlig", "public"),
                Choice("Begrenset offentlighet", "restricted"),
                Choice("Unntatt offentlighet", "non-public"),
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
            "when": lambda x: include_extra_metadata,
        },
        {"type": "text", "name": "name", "message": "Kontaktperson – navn"},
        {
            **required_style,
            "type": "text",
            "name": "email",
            "message": "Kontaktperson – epost",
            "validate": SimpleEmailValidator,
        },
        {
            **required_style,
            "type": "text",
            "name": "phone",
            "message": "Kontaktperson – telefon",
            "validate": PhoneValidator,
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
