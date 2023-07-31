from starlette.requests import Request
from starlette.responses import Response
from starlette.responses import JSONResponse
from starlette.routing import Route

from eddrit import __version__
from eddrit.templates import templates


async def about(request: Request) -> Response:
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
        },
    )


async def version(request: Request) -> Response:
    return JSONResponse({"version": __version__})


routes = [
    Route("/about", endpoint=about),
    Route("/version", endpoint=version),
]
