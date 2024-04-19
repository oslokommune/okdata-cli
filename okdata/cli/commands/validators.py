import csv
import datetime
import re
from types import SimpleNamespace
from urllib.parse import urlparse

from questionary import Validator, ValidationError

# Validators for questionary
# We don't want to make these too complicated for now, but implement
# a base validation to get content for the dataset and pipeline
# questionary is only interested in the ValidationError, no return values needed


class DateValidator(Validator):
    def validate(self, document):
        try:
            datetime.datetime.strptime(document.text, "%Y-%m-%d")
        except ValueError:
            raise ValidationError(
                message="Please enter a valid date in format YYYY-MM-DD, example: 2020-05-01)",
                cursor_position=len(document.text),
            )


class SimpleEmailValidator(Validator):
    def validate(self, document):
        # Just check for a "." after a "@"
        if not re.match(r"[^@]+@[^@]+\.[^@]+", document.text):
            raise ValidationError(
                message="Please enter a valid email, example: user@example.org",
                cursor_position=len(document.text),
            )


class TitleValidator(Validator):
    def validate(self, document):
        if len(document.text) < 5:
            raise ValidationError(
                message="Title must be at least 5 characters",
                cursor_position=len(document.text),
            )
        if not re.match(r"^[- a-zA-Z0-9åÅæÆøØ]+$", document.text):
            raise ValidationError(
                message="Title may only contain letters, numbers, spaces, and dashes",
                cursor_position=len(document.text),
            )


class KeywordValidator(Validator):
    def validate(self, document):
        keywords = csv.reader(
            [document.text], delimiter=",", escapechar="\\", skipinitialspace=True
        )
        keywords = [x.strip() for x in next(keywords)]
        have_valid_keywords = keywords and all([len(k) >= 3 for k in keywords])
        if not have_valid_keywords or len(keywords) != len(set(keywords)):
            raise ValidationError(
                message="At least one keyword, each must be unique and at least 3 characters",
                cursor_position=len(document.text),
            )


class IntegrationValidator(Validator):
    def validate(self, document):
        if len(document.text) > 30:
            raise ValidationError(
                message="Too long!", cursor_position=len(document.text)
            )
        if not re.fullmatch("[0-9a-z-]+", document.text):
            raise ValidationError(
                message='Only lowercase letters, numbers and "-", please',
                cursor_position=len(document.text),
            )


class AWSAccountValidator(Validator):
    def validate(self, document):
        if not re.fullmatch("[0-9]{12}", document.text):
            raise ValidationError(
                message="12 digits, please", cursor_position=len(document.text)
            )


class URIValidator(Validator):
    def validate(self, document):
        parsed = urlparse(document.text)

        if not (parsed.scheme and parsed.netloc):
            raise ValidationError(
                message="Please enter a valid URI, including scheme (e.g. https://...)",
                cursor_position=len(document.text),
            )


class URIListValidator(Validator):
    def validate(self, document):
        uri_validator = URIValidator()
        try:
            for val in document.text.split(","):
                uri_validator.validate(SimpleNamespace(text=val))
        except ValidationError:
            raise ValidationError(
                message=(
                    "Please enter a comma-separated list of URIs, including scheme "
                    "(e.g. https://...)"
                ),
                cursor_position=len(document.text),
            )
