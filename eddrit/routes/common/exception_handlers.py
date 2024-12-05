from typing import Any

from starlette.responses import Response

from eddrit.routes.common.context import get_templates_common_context
from eddrit.templates import templates


async def http_exception(request: Any, exc: Exception) -> Response:
    # If it's an HTTPException or an RedditContentUnavailableError
    # there should be a status_code
    status_code = exc.status_code if hasattr(exc, "status_code") else 500  # type: ignore

    # Same for the detail
    detail = exc.detail if hasattr(exc, "detail") else None  # type: ignore
    return templates.TemplateResponse(
        "error.html",
        {
            **get_templates_common_context(request),
            "request": request,
            "status_code": status_code,
            "detail": detail,
        },
        status_code=status_code,
    )
