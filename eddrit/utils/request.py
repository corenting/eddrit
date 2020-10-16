from typing import Any

from starlette.responses import RedirectResponse


def should_redirect_to_age_check(request: Any, over18: bool) -> bool:
    return over18 and request.cookies.get("over18", "0") != "1"


def redirect_to_age_check(request: Any) -> RedirectResponse:
    return RedirectResponse(url="/over18?dest=" + str(request.url))


def get_checkbox_from_form(form_data: Any, name: str) -> bool:
    content = form_data.get(name, "off")

    return content == "on"
