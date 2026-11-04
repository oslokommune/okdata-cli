from types import SimpleNamespace

import pytest
from questionary import ValidationError

from okdata.cli.commands.validators import (
    AWSAccountValidator,
    IntegrationValidator,
    URIListValidator,
    URIValidator,
)

# Note: no testing of return values since the validator is only
# interested in ValidationError occurrences


class TestIntegrationValidator:
    def validate_document(self, data):
        validator = IntegrationValidator()
        document = SimpleNamespace(**data)
        validator.validate(document)

    def test_valid_integrations(self):
        self.validate_document({"text": "x"})
        self.validate_document({"text": "a-b-c-1-2-3"})
        self.validate_document({"text": "q3v3avjd40dmpwicg7kn3xo8drbslu"})
        self.validate_document({"text": "foo bar"})
        self.validate_document({"text": "Foobar"})
        self.validate_document({"text": "blåbærsyltetøy"})
        self.validate_document({"text": "BLÅBÆRSYLTETØY"})

    def test_invalid_integrations(self):
        with pytest.raises(ValidationError):
            self.validate_document({"text": ""})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "foo_bar"})
        with pytest.raises(ValidationError):
            self.validate_document({"text": "foobar😅"})
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
