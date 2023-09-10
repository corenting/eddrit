from typing import Any

from starlette.responses import RedirectResponse


def should_redirect_to_age_check(request: Any, over18: bool) -> bool:
    return over18 and request.cookies.get("over18", "0") != "1"


def redirect_to_age_check(request: Any) -> RedirectResponse:
    return RedirectResponse(url=f"/over18?dest={request.url!s}")
