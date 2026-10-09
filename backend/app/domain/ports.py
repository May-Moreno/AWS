"""Puertos: contratos que la infraestructura debe cumplir."""
from abc import ABC, abstractmethod

from .entities import TokenClaims, User


class UserRepository(ABC):
    @abstractmethod
    def get_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    def list_all(self) -> list[User]: ...


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, password: str) -> str: ...

    @abstractmethod
    def verify(self, password: str, password_hash: str) -> bool: ...


class TokenService(ABC):
    @abstractmethod
    def issue(self, user: User) -> tuple[str, int]:
        """Devuelve (token, segundos_de_vida)."""

    @abstractmethod
    def decode(self, token: str) -> TokenClaims:
        """Lanza InvalidToken si el token no es válido."""


class LoginRateLimiter(ABC):
    @abstractmethod
    def check(self, key: str) -> None:
        """Lanza TooManyAttempts si se excede el límite."""

    @abstractmethod
    def register_failure(self, key: str) -> None: ...

    @abstractmethod
    def reset(self, key: str) -> None: ...
