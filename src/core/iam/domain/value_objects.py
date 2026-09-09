import re
from dataclasses import dataclass

from src.core.iam.domain.exceptions import (
    EmailRequiredError,
    InvalidEmailFormatError,
    InvalidPasswordError,
    PasswordRequiredError,
)


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        self.validate_required()
        self.validate_format()

    def validate_required(self):
        if not self.value:
            raise EmailRequiredError()

    def validate_format(self):
        email_format = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_format, self.value):
            raise InvalidEmailFormatError()


@dataclass(frozen=True)
class PlainPassword:
    value: str

    def __post_init__(self):
        self.validate_required()
        self.validate_length()

    def validate_required(self):
        if not self.value:
            raise PasswordRequiredError()

    def validate_length(self):
        if len(self.value) < 8:
            raise InvalidPasswordError("Пароль должен быть не менее 8 символов")
        if len(self.value) > 64:
            raise InvalidPasswordError("Пароль должен быть не более 64 символов")


@dataclass(frozen=True)
class HashedPassword:
    value: str

    def __post_init__(self):
        self.validate_required()

    def validate_required(self):
        if not self.value:
            raise PasswordRequiredError()
