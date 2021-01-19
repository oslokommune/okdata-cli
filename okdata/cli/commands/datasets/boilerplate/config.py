import csv
from questionary import Choice, prompt
from prompt_toolkit.styles import Style

from .validator import (
    KeywordValidator,
    PhoneValidator,
    SimpleEmailValidator,
    TitleValidator,
    StandardsValidator,
    SpatialValidator,
    SpatialResolutionValidator,
)

required_style = Style([("qmark", "fg:red bold")])

pipeline_choices = [
    Choice("Lagre dataen slik den er", "data-copy"),
    Choice("Konverter fra CSV til Parquet", "csv-to-parquet"),
    Choice("Konverter fra Excel til CSV", "pipeline-excel-to-csv"),
    Choice("Ingen prosessering (krever manuell konfigurasjon av pipeline)", False),
]

available_pipelines = [c.value for c in pipeline_choices if c.value]


def filter_comma_separated(value):
    values = next(
        csv.reader([value], delimiter=",", escapechar="\\", skipinitialspace=True)
    )
    return [x.strip() for x in values if x]


def boilerplate_prompt(include_extra_metadata=True):
    boilerplate_questions = [
        {
            "type": "text",
            "qmark": "*",
            "style": required_style,
            "name": "title",
            "message": "Tittel",
            "validate": TitleValidator,
        },
        {"type": "text", "name": "description", "message": "Beskrivelse"},
        {"type": "text", "name": "objective", "message": "Formål"},
        {
            "type": "text",
            "qmark": "*",
            "style": required_style,
            "name": "keywords",
            "message": "Nøkkelord (komma-separert)",
            "validate": KeywordValidator,
            "filter": filter_comma_separated,
        },
        {
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
            "type": "select",
            "qmark": "*",
            "style": required_style,
            "name": "accessRights",
            "message": "Tilgangsnivå",
            "choices": [
                Choice("Offentlig", "public"),
                Choice("Begrenset offentlighet", "restricted"),
                Choice("Unntatt offentlighet", "non-public"),
            ],
        },
        {
            "type": "text",
            "name": "license",
            "message": "Lisens",
            "filter": lambda v: v.strip(),
            "when": lambda x: include_extra_metadata,
        },
        {"type": "text", "name": "name", "message": "Kontaktperson - navn"},
        {
            "type": "text",
            "qmark": "*",
            "style": required_style,
            "name": "email",
            "message": "Kontaktperson - epost",
            "validate": SimpleEmailValidator,
        },
        {
            "type": "text",
            "qmark": "*",
            "style": required_style,
            "name": "phone",
            "message": "Kontaktperson - telefon",
            "validate": PhoneValidator,
        },
        {"type": "text", "name": "publisher", "message": "Utgiver"},
        {
            "type": "select",
            "qmark": "*",
            "style": required_style,
            "name": "pipeline",
            "message": "Prosessering",
            "choices": pipeline_choices,
        },
    ]

    return prompt(boilerplate_questions)
