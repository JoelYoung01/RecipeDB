"""Standardized API error responses with a user-facing message.

All HTTP errors (and unexpected 500s) are normalized to::

    {
      "user_message": "Something a human can read.",
      "detail": <original FastAPI detail — str | dict | list>,
      "code": "<optional machine code>"
    }

`detail` is preserved for structured callers (e.g. auth redirect payloads).
`user_message` is always a string suitable for toasts / inline UI.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.core.config import settings

logger = logging.getLogger(__name__)

DEFAULT_USER_MESSAGES: dict[int, str] = {
    400: "That request wasn’t valid. Please check and try again.",
    401: "Please sign in to continue.",
    403: "You don’t have permission to do that.",
    404: "We couldn’t find what you were looking for.",
    409: "That conflicts with existing data.",
    422: "Some of the information provided isn’t valid.",
    429: "Too many attempts. Please wait a moment and try again.",
    500: "Something went wrong on our end. Please try again.",
    502: "A dependent service failed. Please try again.",
    503: "The service is temporarily unavailable. Please try again.",
}


def _message_from_detail(detail: Any, status_code: int) -> str:
    if isinstance(detail, str) and detail.strip():
        return detail.strip()

    if isinstance(detail, dict):
        for key in ("user_message", "message"):
            value = detail.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        code = detail.get("code")
        if isinstance(code, str) and code.strip():
            return code.replace("_", " ").strip().capitalize()

    if isinstance(detail, list) and detail:
        parts: list[str] = []
        for item in detail[:3]:
            if isinstance(item, dict):
                msg = item.get("msg") or item.get("message")
                loc = item.get("loc")
                if isinstance(msg, str):
                    if isinstance(loc, (list, tuple)) and len(loc) > 1:
                        field = ".".join(str(x) for x in loc if x != "body")
                        parts.append(f"{field}: {msg}" if field else msg)
                    else:
                        parts.append(msg)
            elif isinstance(item, str):
                parts.append(item)
        if parts:
            return "; ".join(parts)

    return DEFAULT_USER_MESSAGES.get(
        status_code, "Something went wrong. Please try again."
    )


def _code_from_detail(detail: Any) -> str | None:
    if isinstance(detail, dict):
        code = detail.get("code")
        if isinstance(code, str) and code.strip():
            return code.strip()
    return None


def error_body(status_code: int, detail: Any = None) -> dict[str, Any]:
    """Build the standardized error JSON body."""
    body: dict[str, Any] = {
        "user_message": _message_from_detail(detail, status_code),
        "detail": (
            detail if detail is not None else DEFAULT_USER_MESSAGES.get(status_code)
        ),
    }
    code = _code_from_detail(detail)
    if code:
        body["code"] = code
    return body


def error_response(
    status_code: int,
    detail: Any = None,
    *,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=error_body(status_code, detail),
        headers=headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        # SPA fallback for unknown non-API routes in deployed builds.
        if (
            exc.status_code == 404
            and settings.ENVIRONMENT != "development"
            and not request.url.path.startswith(settings.API_V1_STR)
            and not request.url.path.startswith("/uploads/")
        ):
            from fastapi.responses import FileResponse

            return FileResponse(f"{settings.VUE_STATIC_DIR}/index.html")

        return error_response(exc.status_code, exc.detail, headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError):
        return error_response(422, exc.errors())

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception):
        logger.exception("Unhandled server error")
        if settings.ENVIRONMENT == "development":
            detail = f"{type(exc).__name__}: {exc}"
        else:
            detail = DEFAULT_USER_MESSAGES[500]
        return error_response(500, detail)
