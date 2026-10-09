"""Casos de uso. Dependen solo de puertos del dominio."""
import logging

from ..domain.entities import User
from ..domain.errors import InvalidCredentials, InvalidToken, PermissionDenied
from ..domain.ports import LoginRateLimiter, PasswordHasher, TokenService, UserRepository

audit = logging.getLogger("audit")


class AuthService:
    def __init__(self, users: UserRepository, hasher: PasswordHasher,
                 tokens: TokenService, limiter: LoginRateLimiter):
        self._users = users
        self._hasher = hasher
        self._tokens = tokens
        self._limiter = limiter
        # Hash señuelo: iguala el tiempo de respuesta cuando el usuario no existe.
        self._dummy_hash = hasher.hash("señuelo-no-valido")

    def login(self, username: str, password: str, client_ip: str) -> tuple[str, int]:
        key = f"{client_ip}:{username.lower()}"
        self._limiter.check(key)
        user = self._users.get_by_username(username)
        hash_to_check = user.password_hash if user else self._dummy_hash
        valid = self._hasher.verify(password, hash_to_check)
        if not (user and user.active and valid):
            self._limiter.register_failure(key)
            audit.warning("login_fallido user=%s ip=%s", username, client_ip)
            raise InvalidCredentials("Credenciales inválidas")
        self._limiter.reset(key)
        audit.info("login_ok user=%s ip=%s", username, client_ip)
        return self._tokens.issue(user)

    def authenticate(self, token: str) -> User:
        """Verifica el token EN CADA solicitud y revalida al usuario contra el repositorio."""
        claims = self._tokens.decode(token)
        user = self._users.get_by_username(claims.username)
        if not user or not user.active or user.role != claims.role:
            raise InvalidToken("Token no válido")
        return user

    @staticmethod
    def authorize(user: User, permission: str) -> None:
        if not user.has_permission(permission):
            audit.warning("acceso_denegado user=%s permiso=%s", user.username, permission)
            raise PermissionDenied(permission)


class DashboardService:
    def summary(self, user: User) -> dict:
        AuthService.authorize(user, "dashboard:read")
        return {
            "user": user.username,
            "role": user.role,
            "metrics": [
                {"label": "Solicitudes validadas", "value": 1280},
                {"label": "Accesos denegados", "value": 14},
                {"label": "Sesiones activas", "value": 7},
            ],
        }

    def list_users(self, user: User, users: list[User]) -> list[dict]:
        AuthService.authorize(user, "users:read")
        return [{"username": u.username, "role": u.role, "active": u.active} for u in users]
