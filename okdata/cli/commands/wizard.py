import csv
import sys

from prompt_toolkit.styles import Style
from questionary import prompt

required_style = {
    "qmark": "*",
    "style": Style([("qmark", "fg:red bold")]),
}


def run_questionnaire(*questions):
    choices = prompt(questions)

    if not choices:
        # Questionnaire was interrupted.
        sys.exit()

    return choices


def filter_comma_separated(value):
    values = next(
        csv.reader([value], delimiter=",", escapechar="\\", skipinitialspace=True)
    )
    return [x.strip() for x in values if x]
