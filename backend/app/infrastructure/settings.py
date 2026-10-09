import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    env: str
    secret_key: str
    access_token_minutes: int
    admin_password: str
    analyst_password: str
    cors_origins: list[str]
    jwt_issuer: str = "zt-backend"
    jwt_audience: str = "zt-frontend"


def load_settings() -> Settings:
    secret = os.environ.get("SECRET_KEY", "")
    if len(secret) < 32:
        raise RuntimeError("SECRET_KEY debe tener al menos 32 caracteres")
    origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()]
    return Settings(
        env=os.environ.get("ENV", "prod"),
        secret_key=secret,
        access_token_minutes=int(os.environ.get("ACCESS_TOKEN_MINUTES", "15")),
        admin_password=os.environ["ADMIN_PASSWORD"],
        analyst_password=os.environ["ANALYST_PASSWORD"],
        cors_origins=origins,
    )
