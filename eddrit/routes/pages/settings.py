from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from eddrit.routes.common.context import get_templates_common_context
from eddrit.routes.common.cookies import get_default_cookie_settings
from eddrit.templates import templates


async def settings_page(request: Request) -> Response:
    return templates.TemplateResponse(
        "settings.html",
        get_templates_common_context(request),
    )


async def settings_submit(request: Request) -> Response:
    # Get request content
    data = await request.form()

    # For each modified setting, prepare cookies
    updated_cookies: dict[str, str] = {}
    for setting_key, setting_value in data.items():
        # If it's a checkbox it's on or off
        # and we can set directly
        if setting_value in ["on", "off"]:
            value_to_save = "1" if setting_value == "on" else "0"
        # Else it's a radio, save value directly (with lower for theme)
        else:
            value_to_save = str(setting_value)

        updated_cookies[setting_key] = value_to_save

    res = templates.TemplateResponse(
        "settings.html",
        {
            **get_templates_common_context(request, request.cookies | updated_cookies),
            "is_saved": True,
        },
    )

    default_cookie_settings = get_default_cookie_settings()
    for cookie_name, cookie_value in updated_cookies.items():
        res.set_cookie(
            cookie_name,
            cookie_value,
            secure=default_cookie_settings.secure,
            httponly=default_cookie_settings.http_only,
            expires=default_cookie_settings.expiration_date,
        )

    return res


routes = [
    Route("/settings", endpoint=settings_page, methods=["GET"]),
    Route("/settings", endpoint=settings_submit, methods=["POST"]),
]
