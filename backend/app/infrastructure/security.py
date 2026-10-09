import time
import uuid

import bcrypt
import jwt

from ..domain.entities import TokenClaims, User
from ..domain.errors import InvalidToken
from ..domain.ports import PasswordHasher, TokenService


class BcryptHasher(PasswordHasher):
    def hash(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

    def verify(self, password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode(), password_hash.encode())
        except ValueError:
            return False


class JwtTokenService(TokenService):
    ALGORITHM = "HS256"

    def __init__(self, secret: str, minutes: int, issuer: str, audience: str):
        self._secret = secret
        self._ttl = minutes * 60
        self._issuer = issuer
        self._audience = audience

    def issue(self, user: User) -> tuple[str, int]:
        now = int(time.time())
        payload = {
            "sub": user.username, "role": user.role,
            "iss": self._issuer, "aud": self._audience,
            "iat": now, "exp": now + self._ttl, "jti": uuid.uuid4().hex,
        }
        return jwt.encode(payload, self._secret, algorithm=self.ALGORITHM), self._ttl

    def decode(self, token: str) -> TokenClaims:
        try:
            data = jwt.decode(
                token, self._secret, algorithms=[self.ALGORITHM],  # algoritmo fijo
                audience=self._audience, issuer=self._issuer,
                options={"require": ["exp", "iat", "sub", "iss", "aud", "jti"]},
            )
        except jwt.PyJWTError as exc:
            raise InvalidToken("Token no válido") from exc
        return TokenClaims(data["sub"], data.get("role", ""), data["jti"], data["exp"])
