import pytest
from types import SimpleNamespace
from questionary import ValidationError

from okdata.cli.commands.datasets.boilerplate.validator import (
    DateValidator,
    KeywordValidator,
    PhoneValidator,
    SimpleEmailValidator,
    TitleValidator,
    StandardsValidator,
    SpatialValidator,
    SpatialResolutionValidator,
)

# Note: no testing of return values since the validator is only
# interested in ValidationError occurences


class TestDateValidator:
    def validate_document(self, data):
        validator = DateValidator()
        document = SimpleNamespace(**data)
        validator.validate(document)

    def test_incomplete_date(self):
        with pytest.raises(ValidationError):
            self.validate_document({"text": "2020-01-"})

    def test_invalid_input(self):
        with pytest.raises(ValidationError):
            self.validate_document({"text": "2020-01-ab"})

    def test_empty_date(self):
        with pytest.raises(ValidationError):
            self.validate_document({"text": ""})


class TestSimpleEmailValidator:
    def validate_email(self, data):
        validator = SimpleEmailValidator()
        document = SimpleNamespace(**data)
        validator.validate(document)

    def test_incomplete_email(self):
        with pytest.raises(ValidationError):
            self.validate_email({"text": "test@example"})

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            self.validate_email({"text": "just random text"})

    def test_empty_email(self):
        with pytest.raises(ValidationError):
            self.validate_email({"text": ""})


class TestPhoneValidator:
    def validate_phone(self, data):
        validator = PhoneValidator()
        document = SimpleNamespace(**data)
        validator.validate(document)

    def test_phone_with_space(self):
        with pytest.raises(ValidationError):
            self.validate_phone({"text": " 22334455"})

    def test_invalid_phone(self):
        with pytest.raises(ValidationError):
            self.validate_phone({"text": "2233b4455"})

    def test_empty_email(self):
        with pytest.raises(ValidationError):
            self.validate_phone({"text": ""})


class TestTitleValidator:
    def validate_title(self, data):
        validator = TitleValidator()
        document = SimpleNamespace(**data)
        validator.validate(document)

    def test_too_short_title(self):
        with pytest.raises(ValidationError):
            self.validate_title({"text": "abc"})

    def test_empty_title(self):
        with pytest.raises(ValidationError):
            self.validate_title({"text": ""})


class TestKeywordValidator:
    def validate_keywords(self, data):
        validator = KeywordValidator()
        document = SimpleNamespace(**data)
        validator.validate(document)

    def test_too_short_keywords(self):
        with pytest.raises(ValidationError):
            self.validate_keywords({"text": "ab, cd"})

    def test_one_valid_and_one_invalid_keyword(self):
        with pytest.raises(ValidationError):
            self.validate_keywords({"text": "abc, cd"})

    def test_one_invalid_and_one_valid_keyword(self):
        with pytest.raises(ValidationError):
            self.validate_keywords({"text": "cd, abc"})

    def test_empty_keywords(self):
        with pytest.raises(ValidationError):
            self.validate_keywords({"text": ""})


class TestStandardsValidator:
    def validate_document(self, data):
        validator = StandardsValidator()
        document = SimpleNamespace(**data)
        validator.validate(document)

    def test_valid(self):
        self.validate_document({"text": "abc"})
        self.validate_document({"text": "http://www.opengis.net/def/crs/EPSG/0/5972"})
        self.validate_document({"text": "abc\ndefg"})

    def test_empty(self):
        self.validate_document({"text": ""})
        self.validate_document({"text": "\n\n\n"})

    def test_min_length(self):
        with pytest.raises(ValidationError):
            self.validate_document({"text": "a"})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "a\n\nc\nd"})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "\n\nc\nd"})

    def test_one_invalid_and_one_valid_value(self):
        with pytest.raises(ValidationError):
            self.validate_document({"text": "a\nstandarddokument"})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "standarddokument\nab"})


class TestSpatialValidator:
    def validate_document(self, data):
        validator = SpatialValidator()
        document = SimpleNamespace(**data)
        validator.validate(document)

    def test_valid(self):
        self.validate_document({"text": "Oslo"})
        self.validate_document({"text": "Oslo Bydel 1\nOslo Bydel 2"})

    def test_empty(self):
        self.validate_document({"text": ""})
        self.validate_document({"text": "\n\n\n"})

    def test_one_invalid_and_one_valid_value(self):
        with pytest.raises(ValidationError):
            self.validate_document({"text": "Å\n"})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "\nÅs"})


class TestSpatialResolutionValidator:
    def validate_document(self, data):
        validator = SpatialResolutionValidator()
        document = SimpleNamespace(**data)
        validator.validate(document)

    def test_valid_numbers(self):
        self.validate_document({"text": "1"})
        self.validate_document({"text": "1.234"})
        self.validate_document({"text": "1,234"})
        self.validate_document({"text": "0,234"})

    def test_invalid_separator(self):
        with pytest.raises(ValidationError):
            self.validate_document({"text": "1-234"})

    def test_gt_zero(self):
        with pytest.raises(ValidationError):
            self.validate_document({"text": "0"})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "-1.2"})

    def test_invalid_value(self):
        with pytest.raises(ValidationError):
            self.validate_document({"text": "ukjent"})
