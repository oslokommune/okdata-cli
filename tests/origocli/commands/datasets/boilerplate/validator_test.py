import pytest
from types import SimpleNamespace
from questionary import ValidationError

from okdata.cli.commands.datasets.boilerplate.validator import (
    DateValidator,
    KeywordValidator,
    PhoneValidator,
    SimpleEmailValidator,
    TitleValidator,
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
