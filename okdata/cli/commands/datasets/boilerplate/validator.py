import re
import csv
import datetime

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


class TitleValidator(Validator):
    def validate(self, document):
        if len(document.text) < 5:
            raise ValidationError(
                message="Title must be at least 5 characters",
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


class StandardsValidator(Validator):
    def validate(self, document):
        standards = csv.reader(
            [document.text], delimiter=",", escapechar="\\", skipinitialspace=True
        )
        standards = [x.strip() for x in next(standards)]
        for standard in standards:
            if len(standard) < 3:
                raise ValidationError(
                    message="Each standard reference must be at least 3 characters",
                    cursor_position=len(document.text),
                )
        if len(standards) != len(set(standards)):
            raise ValidationError(
                message="Each standard reference must be unique",
                cursor_position=len(document.text),
            )


class SpatialValidator(Validator):
    def validate(self, document):
        locations = csv.reader(
            [document.text], delimiter=",", escapechar="\\", skipinitialspace=True
        )
        locations = [x.strip() for x in next(locations)]
        for location in locations:
            if len(location) < 1:
                raise ValidationError(
                    message="Each location must be at least 1 character",
                    cursor_position=len(document.text),
                )
        if len(locations) != len(set(locations)):
            raise ValidationError(
                message="Each location must be unique",
                cursor_position=len(document.text),
            )


class SpatialResolutionValidator(Validator):
    def validate(self, document):
        if not document.text:
            return None
        try:
            number = float(document.text.replace(",", "."))
            if number <= 0:
                raise ValueError
        except ValueError:
            raise ValidationError(
                message="Please enter a positive (decimal) number",
                cursor_position=len(document.text),
            )
        return None
