from questionary import Choice

from .validator import (
    KeywordValidator,
    PhoneValidator,
    SimpleEmailValidator,
    TitleValidator,
)

available_pipelines = ["data-copy", "csv-to-parquet"]
boilerplate_questions = [
    {"type": "text", "name": "title", "message": "Tittel", "validate": TitleValidator},
    {"type": "text", "name": "description", "message": "Beskrivelse"},
    {"type": "text", "name": "objective", "message": "Formål"},
    {
        "type": "text",
        "name": "keywords",
        "message": "Nøkkelord (komma-separert)",
        "validate": KeywordValidator,
    },
    {
        "type": "select",
        "name": "accessRights",
        "message": "Tilgangsnivå",
        "choices": [
            Choice("Offentlig", "public"),
            Choice("Begrenset offentlighet", "restricted"),
            Choice("Unntatt offentlighet", "non-public"),
        ],
    },
    {"type": "text", "name": "name", "message": "Kontaktperson - navn"},
    {
        "type": "text",
        "name": "email",
        "message": "Kontaktperson - epost",
        "validate": SimpleEmailValidator,
    },
    {
        "type": "text",
        "name": "phone",
        "message": "Kontaktperson - telefon",
        "validate": PhoneValidator,
    },
    {"type": "text", "name": "publisher", "message": "Utgiver"},
    {
        "type": "select",
        "name": "pipeline",
        "message": "Prosessering",
        "choices": available_pipelines,
    },
]
