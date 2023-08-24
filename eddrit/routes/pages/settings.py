from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from eddrit import models
from eddrit.config import DEBUG
from eddrit.routes.common.context import get_templates_common_context
from eddrit.templates import templates
from eddrit.utils.request import get_checkbox_from_form


async def settings_page(request: Request) -> Response:
    return templates.TemplateResponse(
        "settings.html",
        get_templates_common_context(request),
    )


async def settings_submit(request: Request) -> Response:
    # Get request content
    data = await request.form()
    nsfw_popular_all = get_checkbox_from_form(data, "nsfw_popular_all")
    nsfw_thumbnails = get_checkbox_from_form(data, "nsfw_thumbnails")

    res = templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "is_saved": True,
            "settings": models.Settings(
                nsfw_popular_all=nsfw_popular_all,
                nsfw_thumbnails=nsfw_thumbnails,
            ),
        },
    )

    # Set cookies for response
    boolean_cookies = [
        ("nsfw_popular_all", nsfw_popular_all),
        ("nsfw_thumbnails", nsfw_thumbnails),
    ]
    for cookie_name, cookie_value in boolean_cookies:
        res.set_cookie(
            cookie_name,
            "1" if cookie_value else "0",
            secure=not DEBUG,
            httponly=True,
        )
    return res


routes = [
    Route("/settings", endpoint=settings_page, methods=["GET"]),
    Route("/settings", endpoint=settings_submit, methods=["POST"]),
]
