from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route


async def robots_txt(request: Request) -> Response:
    return Response(
        "User-agent: *\nDisallow: /",
        media_type="text/plain",
    )


routes = [
    Route("/robots.txt", endpoint=robots_txt, methods=["GET"]),
]
