from ..domain.entities import User
from ..domain.ports import PasswordHasher, UserRepository


class InMemoryUserRepository(UserRepository):
    """Adaptador de persistencia. Sustituible por SQL sin tocar dominio ni casos de uso."""

    def __init__(self, hasher: PasswordHasher, admin_password: str, analyst_password: str):
        self._users = {
            "admin": User("admin", hasher.hash(admin_password), "admin"),
            "analista": User("analista", hasher.hash(analyst_password), "analyst"),
        }

    def get_by_username(self, username: str) -> User | None:
        return self._users.get(username.lower())

    def list_all(self) -> list[User]:
        return list(self._users.values())
