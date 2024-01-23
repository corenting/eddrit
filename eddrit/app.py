import contextlib
import typing

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from eddrit import __version__, config
from eddrit.routes.common import exception_handlers
from eddrit.routes.pages import (
    index,
    meta,
    over18,
    root_files,
    search,
    settings,
    subreddit_and_user,
)
from eddrit.routes.xhr import routes
from eddrit.utils.httpx import raise_if_rate_limited
from eddrit.utils.middlewares import CurrentHostMiddleware, NoReferrerMiddleware

middlewares = [
    Middleware(NoReferrerMiddleware),
    Middleware(CurrentHostMiddleware),
]

exceptions_handlers = {
    HTTPException: exception_handlers.http_exception,
    500: exception_handlers.http_exception,  # 500 are handled separately by starlette
}


class State(typing.TypedDict):
    """App state"""

    http_client: httpx.AsyncClient


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> typing.AsyncIterator[State]:
    """Init the app lifespan with httpx client."""

    async with httpx.AsyncClient(
        headers={"User-Agent": f"eddrit:v{__version__}"},
        http2=True,
        event_hooks={"response": [raise_if_rate_limited]},
    ) as client:
        yield {"http_client": client}


app = Starlette(
    lifespan=lifespan,
    debug=config.DEBUG,
    routes=[
        Mount("/static", app=StaticFiles(directory="static"), name="static"),
        Mount("/meta", routes=meta.routes, name="meta"),
        Mount("/r", routes=subreddit_and_user.routes, name="subreddit"),
        Mount("/user", routes=subreddit_and_user.routes, name="user"),
        Mount("/xhr", routes=routes, name="api"),
        Mount(
            "/",
            routes=[
                *search.routes,
                *root_files.routes,
                *over18.routes,
                *settings.routes,
                *index.routes,
            ],
            name="root",
        ),
    ],
    middleware=middlewares,
    exception_handlers=exceptions_handlers,  # type: ignore
)

if __name__ == "__main__":
    uvicorn.run(
        "app:app", host="0.0.0.0", port=8000, reload=True, log_level=config.LOG_LEVEL
    )
