from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Route

from eddrit.templates import templates


async def check_page(request: Request) -> Response:
    can_proceed = request.cookies.get("over18", "0") == "1"
    destination_link = request.query_params.get("dest", None)

    if can_proceed:
        if destination_link:
            pass
        else:
            return RedirectResponse(url="/")

    return templates.TemplateResponse(
        "over18.html", {"request": request, "destination_link": destination_link,}
    )


async def check_submit(request: Request) -> Response:
    body = await request.form()
    continue_url = body.get("continue", "/")
    res = RedirectResponse(url=continue_url, status_code=302)
    res.set_cookie("over18", "1", secure=True, httponly=True)
    return res


routes = [
    Route("/over18", endpoint=check_page, methods=["GET"]),
    Route("/over18", endpoint=check_submit, methods=["POST"]),
]
