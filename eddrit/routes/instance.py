from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from eddrit import __version__


async def version(request: Request) -> Response:
    return JSONResponse({"version": __version__})


routes = [
    Route("/version", endpoint=version),
]
