import pytest

from src.core.iam.domain.exceptions import (
    EmailRequiredError,
    InvalidEmailFormatError,
    InvalidPasswordError,
    PasswordRequiredError,
)
from src.core.iam.domain.value_objects import Email, HashedPassword, PlainPassword


class TestEmailValueObject:
    @pytest.mark.unit
    def test_successful_email_creation(self):
        email = Email(value="test@example.com")
        assert email.value == "test@example.com"

    @pytest.mark.unit
    def test_email_required_raises(self):
        with pytest.raises(EmailRequiredError):
            Email(value=None)

    @pytest.mark.unit
    def test_email_format_raises(self):
        with pytest.raises(InvalidEmailFormatError):
            Email(value="test")


class TestPlainPasswordValueObject:
    @pytest.mark.unit
    def test_successful_plain_password_creation(self):
        plain_password = PlainPassword(value="myPassword321")
        assert plain_password.value == "myPassword321"

    @pytest.mark.unit
    def test_plain_required_raises(self):
        with pytest.raises(PasswordRequiredError):
            PlainPassword(value=None)

    @pytest.mark.unit
    def test_plain_password_length_raises(self):
        with pytest.raises(InvalidPasswordError):
            PlainPassword(value="psw123")


class TestPasswordValueObject:
    @pytest.mark.unit
    def test_successful_password_creation(self):
        password = HashedPassword(value="hashed_password")
        assert password.value is not None

    @pytest.mark.unit
    def test_password_required_raises(self):
        with pytest.raises(PasswordRequiredError):
            HashedPassword(value=None)
