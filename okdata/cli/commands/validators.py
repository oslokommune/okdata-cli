import re
from types import SimpleNamespace
from urllib.parse import urlparse

from questionary import Validator, ValidationError

# Validators for questionary.
#
# We don't want to make these too complicated for now, but implement a base
# validation to get content for the wizards. Questionary is only interested in
# the `ValidationError`, so no return values are needed.


class IntegrationValidator(Validator):
    def validate(self, document):
        if len(document.text) > 30:
            raise ValidationError(
                message="Too long!", cursor_position=len(document.text)
            )
        if not re.fullmatch("[0-9a-zA-ZæøåÆØÅ -]+", document.text):
            raise ValidationError(
                message='Only letters, numbers, spaces and "-", please',
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
