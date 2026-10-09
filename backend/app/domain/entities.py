"""Dominio puro: sin dependencias de FastAPI, JWT, bcrypt ni base de datos."""
from dataclasses import dataclass

# Mínimo privilegio: cada rol solo tiene los permisos estrictamente necesarios.
ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "analyst": frozenset({"dashboard:read"}),
    "admin": frozenset({"dashboard:read", "users:read"}),
}


@dataclass(frozen=True)
class User:
    username: str
    password_hash: str
    role: str
    active: bool = True

    @property
    def permissions(self) -> frozenset[str]:
        return ROLE_PERMISSIONS.get(self.role, frozenset())

    def has_permission(self, permission: str) -> bool:
        return self.active and permission in self.permissions


@dataclass(frozen=True)
class TokenClaims:
    username: str
    role: str
    jti: str
    expires_at: int
