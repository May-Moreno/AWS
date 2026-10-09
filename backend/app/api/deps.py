import logging

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..domain.entities import User
from ..domain.errors import InvalidToken

bearer = HTTPBearer(auto_error=False)
audit = logging.getLogger("audit")


def get_container(request: Request):
    return request.app.state.container


def current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    container=Depends(get_container),
) -> User:
    """Nunca se confía en la solicitud: el token se valida en cada llamada."""
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No autenticado",
                            headers={"WWW-Authenticate": "Bearer"})
    try:
        return container.auth.authenticate(creds.credentials)
    except InvalidToken:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token no válido",
                            headers={"WWW-Authenticate": "Bearer"})


def require_permission(permission: str):
    def checker(user: User = Depends(current_user)) -> User:
        if not user.has_permission(permission):
            audit.warning("acceso_denegado user=%s permiso=%s", user.username, permission)
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Permiso insuficiente")
        return user
    return checker
