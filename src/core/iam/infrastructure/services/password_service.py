from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from rbloom import Bloom

from src.core.iam.domain.exceptions import InvalidPasswordError
from src.core.iam.domain.value_objects import HashedPassword, PlainPassword


class PasswordService:
    def __init__(self, bloom: Bloom):
        self._bloom = bloom
        self.hasher = PasswordHash([Argon2Hasher()])

    def validate(self, plain_password: str) -> PlainPassword:
        validated_plain = PlainPassword(plain_password)

        if self._bloom is not None and plain_password in self._bloom:
            raise InvalidPasswordError("Ненадежный пароль. Придумайте другой")

        return validated_plain

    def hash(self, plain_password: PlainPassword) -> HashedPassword:
        return HashedPassword(self.hasher.hash(plain_password.value))

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return self.hasher.verify(plain_password, hashed_password)
