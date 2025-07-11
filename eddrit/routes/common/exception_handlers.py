from typing import Any

import httpcore
import httpx
from starlette.responses import Response

from eddrit.routes.common.context import get_templates_common_context
from eddrit.templates import templates


async def http_exception(request: Any, exc: Exception) -> Response:
    """Global exception handler"""
    # If we get an httpx timeout, it probably mean reddit blocked us
    # or is down
    if type(exc) is httpx.ReadTimeout or type(exc) is httpcore.ReadTimeout:
        status_code = 429
        detail = "Cannot fetch content from Reddit: either Reddit is down or eddrit is currently blocked. Try again later or on another instance"
    else:
        # Try to check if there is a status_code or a detail error
        # (for RedditContentUnavailableError and HTTPException)
        status_code = exc.status_code if hasattr(exc, "status_code") else 500  # type: ignore
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
