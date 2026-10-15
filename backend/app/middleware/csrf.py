from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings
from app.services.session_service import csrf_token_matches


UNSAFE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
SESSION_LOGIN_PATH = "/auth/session/login"


def _origin_is_allowed(request: Request) -> bool:
    origin = request.headers.get("origin")
    return bool(origin and origin in settings.cors_origins)


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method not in UNSAFE_METHODS:
            return await call_next(request)

        if request.url.path == SESSION_LOGIN_PATH:
            if not _origin_is_allowed(request):
                return JSONResponse(
                    {"detail": "Request origin is not allowed"},
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            return await call_next(request)

        if request.headers.get("authorization"):
            return await call_next(request)

        session_token = request.cookies.get(settings.SESSION_COOKIE_NAME)
        if session_token is None:
            return await call_next(request)

        if not _origin_is_allowed(request) or not csrf_token_matches(
            session_token,
            request.headers.get(settings.CSRF_HEADER_NAME),
        ):
            return JSONResponse(
                {"detail": "CSRF validation failed"},
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return await call_next(request)
