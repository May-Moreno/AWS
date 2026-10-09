from fastapi import APIRouter, Depends, HTTPException, Request, status

from ..domain.entities import User
from ..domain.errors import InvalidCredentials, TooManyAttempts
from .deps import current_user, get_container, require_permission
from .schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/auth/login", response_model=TokenResponse)
def login(body: LoginRequest, request: Request, container=Depends(get_container)):
    ip = request.client.host if request.client else "desconocido"
    try:
        token, ttl = container.auth.login(body.username, body.password, ip)
    except TooManyAttempts:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Demasiados intentos, espere unos minutos")
    except InvalidCredentials:
        # Mensaje genérico: no revela si el usuario existe.
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario o contraseña incorrectos")
    return TokenResponse(access_token=token, expires_in=ttl)


@router.get("/auth/me")
def me(user: User = Depends(current_user)):
    return {"username": user.username, "role": user.role, "permissions": sorted(user.permissions)}


@router.get("/dashboard/summary")
def dashboard(user: User = Depends(require_permission("dashboard:read")),
              container=Depends(get_container)):
    return container.dashboard.summary(user)


@router.get("/admin/users")
def users(user: User = Depends(require_permission("users:read")),
          container=Depends(get_container)):
    return container.dashboard.list_users(user, container.users.list_all())
