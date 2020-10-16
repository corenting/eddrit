from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from eddrit.templates import templates


async def about(request: Request) -> Response:
    return templates.TemplateResponse("about.html", {"request": request,},)


routes = [
    Route("/about", endpoint=about),
]
