import random
import string
from typing import Self

from django.core.cache import cache


def generate_verification_code(length: int = 6) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


class EmailVerificationCode:
    def __init__(self, email: str, code: str):
        self.email = email
        self.code = code
        self._key = f"verification_code:{self.email}"

    @classmethod
    def generate(cls, email: str) -> Self:
        return cls(email, generate_verification_code())

    def save(self) -> None:
        cache.set(self._key, self.code, timeout=15 * 60)

    @classmethod
    def verify(cls, email: str, code: str) -> bool:
        check_code = cls(email, code)
        stored_code = cache.get(check_code._key)
        if stored_code and stored_code == code:
            cache.delete(check_code._key)
            return True
        return False


verify_msg = """
Thank you for registering! Please verify your email to activate your account.

Your verification code is: {code}

If you did not register for an account, please ignore this email.
"""
