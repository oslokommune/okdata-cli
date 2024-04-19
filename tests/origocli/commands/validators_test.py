from types import SimpleNamespace

import pytest
from questionary import ValidationError

from okdata.cli.commands.validators import (
    AWSAccountValidator,
    DateValidator,
    IntegrationValidator,
    KeywordValidator,
    SimpleEmailValidator,
    TitleValidator,
    URIListValidator,
    URIValidator,
)

# Note: no testing of return values since the validator is only
# interested in ValidationError occurrences


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

    def test_title_with_weird_symbols(self):
        with pytest.raises(ValidationError):
            self.validate_title({"text": "a_b_c (123)"})


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


class TestIntegrationValidator:
    def validate_document(self, data):
        validator = IntegrationValidator()
        document = SimpleNamespace(**data)
        validator.validate(document)

    def test_valid_integrations(self):
        self.validate_document({"text": "x"})
        self.validate_document({"text": "a-b-c-1-2-3"})
        self.validate_document({"text": "q3v3avjd40dmpwicg7kn3xo8drbslu"})

    def test_invalid_integrations(self):
        with pytest.raises(ValidationError):
            self.validate_document({"text": ""})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "foo_bar"})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "foo bar"})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "foobar😅"})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "Foobar"})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "qrmfffqgqzpvlmhmx3vvns3yhlrp9am"})


class TestAWSAccountValidator:
    def validate_document(self, data):
        validator = AWSAccountValidator()
        document = SimpleNamespace(**data)
        validator.validate(document)

    def test_valid_aws_accounts(self):
        self.validate_document({"text": "123456789101"})

    def test_invalid_aws_accounts(self):
        with pytest.raises(ValidationError):
            self.validate_document({"text": ""})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "12345678910"})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "1234567891012"})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "rai3qqvwq8nh"})


class TestURIValidator:
    def validate_document(self, data):
        validator = URIValidator()
        document = SimpleNamespace(**data)
        validator.validate(document)

    def test_valid_uris(self):
        self.validate_document({"text": "http://localhost"})
        self.validate_document({"text": "http://localhost:8000"})
        self.validate_document({"text": "https://example.org"})

    def test_invalid_uris(self):
        with pytest.raises(ValidationError):
            self.validate_document({"text": ""})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "localhost"})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "example.org"})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "http:/localhost"})


class TestURIListValidator:
    def validate_document(self, data):
        validator = URIListValidator()
        document = SimpleNamespace(**data)
        validator.validate(document)

    def test_valid_uri_lists(self):
        self.validate_document({"text": "http://localhost"})
        self.validate_document({"text": "http://localhost,http://localhost:8000"})

    def test_invalid_uri_lists(self):
        with pytest.raises(ValidationError):
            self.validate_document({"text": ""})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "http://localhost,"})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "http://localhost,example.org"})
