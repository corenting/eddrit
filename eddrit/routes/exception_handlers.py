from typing import Any

from starlette.responses import Response

from eddrit.templates import templates


async def http_exception(request: Any, exc: Exception) -> Response:
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 403,
            "detail": exc.detail if hasattr(exc, "detail") else None,  # type: ignore
        },
        status_code=403,
    )
