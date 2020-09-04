import datetime
import re

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


class PhoneValidator(Validator):
    def validate(self, document):
        if not re.match(r"^[0-9]+$", document.text):
            raise ValidationError(
                message="Please enter a valid phone - all numbers and no space, example: 232334455",
                cursor_position=len(document.text),
            )


class EnvironmentValidator(Validator):
    def validate(self, document):
        if not re.match(r"^[0-9]+$", document.text) or len(document.text) != 12:
            raise ValidationError(
                message="Valid environment ID, as provided by Origo, 12 characters. Example: 123456789876",
                cursor_position=len(document.text),
            )


class TitleValidator(Validator):
    def validate(self, document):
        if len(document.text) < 5:
            raise ValidationError(
                message="Title must be at least 5 characters",
                cursor_position=len(document.text),
            )


class KeywordValidator(Validator):
    def validate(self, document):
        keywords = [x.strip() for x in document.text.split(",")]
        if len(keywords) == 0:
            return True
        have_valid_keywords = False
        for keyword in keywords:
            keyword = keyword.strip()
            if len(keyword) >= 3:
                have_valid_keywords = True
            else:
                have_valid_keywords = False
                break
        if have_valid_keywords is False:
            raise ValidationError(
                message="At least one keyword, each must be at least 3 characters",
                cursor_position=len(document.text),
            )
