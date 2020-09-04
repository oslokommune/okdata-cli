from .validator import (
    DateValidator,
    EnvironmentValidator,
    KeywordValidator,
    PhoneValidator,
    SimpleEmailValidator,
    TitleValidator,
)

available_pipelines = ["data-copy", "csv-to-parquet"]
boilerplate_questions = [
    {
        "type": "text",
        "name": "id",
        "message": "Kjøremiljø ID (Som gitt til deg av Origo)",
        "validate": EnvironmentValidator,
    },
    {"type": "text", "name": "title", "message": "Tittel", "validate": TitleValidator},
    {"type": "text", "name": "description", "message": "Beskrivelse"},
    {"type": "text", "name": "objective", "message": "Objektiv"},
    {
        "type": "text",
        "name": "keywords",
        "message": "Nøkkelord (komma-separert)",
        "validate": KeywordValidator,
    },
    {
        "type": "select",
        "name": "accessRights",
        "message": "Tilgang",
        "choices": ["non-public", "public", "restricted"],
    },
    {
        "type": "select",
        "name": "confidentiality",
        "message": "Nivå",
        "choices": ["green", "yellow", "red", "purple"],
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
    {
        "type": "text",
        "name": "startTime",
        "message": "Start tidspunkt for datasett",
        "validate": DateValidator,
    },
    {
        "type": "text",
        "name": "endTime",
        "message": "Slutt tidspunkt for datasett",
        "validate": DateValidator,
    },
]
