"""Composition root: único lugar donde se conectan dominio e infraestructura."""
import logging
from types import SimpleNamespace

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from .application.services import AuthService, DashboardService
from .infrastructure.rate_limiter import InMemoryLoginRateLimiter
from .infrastructure.security import BcryptHasher, JwtTokenService
from .infrastructure.settings import load_settings
from .infrastructure.user_repository import InMemoryUserRepository

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")


def create_app() -> FastAPI:
    s = load_settings()
    hasher = BcryptHasher()
    users = InMemoryUserRepository(hasher, s.admin_password, s.analyst_password)
    tokens = JwtTokenService(s.secret_key, s.access_token_minutes, s.jwt_issuer, s.jwt_audience)
    auth = AuthService(users, hasher, tokens, InMemoryLoginRateLimiter())

    dev = s.env == "dev"
    app = FastAPI(title="Zero Trust API",
                  docs_url="/docs" if dev else None,
                  redoc_url=None, openapi_url="/openapi.json" if dev else None)
    app.state.container = SimpleNamespace(auth=auth, dashboard=DashboardService(), users=users)

    if s.cors_origins:
        app.add_middleware(CORSMiddleware, allow_origins=s.cors_origins,
                           allow_methods=["GET", "POST"],
                           allow_headers=["Authorization", "Content-Type"])

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        resp = await call_next(request)
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Cache-Control"] = "no-store"
        resp.headers["Referrer-Policy"] = "no-referrer"
        return resp

    app.include_router(router)
    return app


app = create_app()
