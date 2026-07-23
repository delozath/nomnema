import pytest

from nomnema.domain.validation.email import (
    is_valid_email,
    raise_valid_email,
)


class TestIsValidEmail:
    @pytest.mark.parametrize(
        ("email"),
        [
            "omar@mail.net",
            "first.last@mail.example.com",
            "user+tag@mail.net",
            "user-name@mail-domain.co",
        ],
    )
    def test_is_valid_email_returns_true_for_well_formed_emails(self, email):
        result = is_valid_email(email)

        assert result is True

    @pytest.mark.parametrize(
        ("email"),
        [
            "plainaddress",
            "missing-domain@",
            "@missingusername.com",
            "user@.com",
            "spaces in@mail.com",
            "",
        ],
    )
    def test_is_valid_email_returns_false_for_malformed_emails(self, email):
        result = is_valid_email(email)

        assert result is False


class TestRaiseValidEmail:
    def test_raise_valid_email_returns_email_when_valid(self):
        email = "omar@mail.net"
        result = raise_valid_email(email)

        assert result == email

    @pytest.mark.parametrize(
        ("email"),
        [
            "plainaddress",
            "missing-domain@",
            "@missingusername.com",
            "",
        ],
    )
    def test_raise_valid_email_raises_value_error_when_invalid(self, email):
        with pytest.raises(ValueError):
            raise_valid_email(email)
