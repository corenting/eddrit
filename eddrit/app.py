import contextlib
import typing
import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette.routing import Route

from eddrit import config
from eddrit.routes.common import exception_handlers
from eddrit.routes.pages import (
    index,
    meta,
    over18,
    root_files,
    search,
    settings,
    subreddit_user_and_wiki,
)
from starlette.responses import RedirectResponse
from eddrit.routes.xhr import routes
from eddrit.utils.middlewares import (
    CookiesRefreshMiddleware,
    CurrentHostMiddleware,
    NoReferrerMiddleware,
)
from eddrit.utils.oauth import (
    oauth_after_request,
    oauth_before_request,
)

middlewares = [
    Middleware(NoReferrerMiddleware),
    Middleware(CurrentHostMiddleware),
    Middleware(
        CookiesRefreshMiddleware,
        cookies_to_refresh=[
            "layout",
            "nsfw_popular_all",
            "nsfw_thumbnails",
            "over18",
            "thumbnails",
        ],
    ),
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
    """Init the app lifespan: httpx client etc.."""
    async with httpx.AsyncClient(
        http2=True,
        event_hooks={
            "request": [oauth_before_request],
            "response": [oauth_after_request],
        },
    ) as client:
        yield {"http_client": client}


def favicon_route(request):
    return RedirectResponse('static/favicon.ico')

app = Starlette(
    lifespan=lifespan,
    debug=config.DEBUG,
    routes=[
        Route("/favicon.ico", endpoint=favicon_route),
        Mount("/static", app=StaticFiles(directory="static"), name="static"),
        Mount("/meta", routes=meta.routes, name="meta"),
        Mount("/r", routes=subreddit_user_and_wiki.routes, name="subreddit"),
        Mount("/user", routes=subreddit_user_and_wiki.routes, name="user"),
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
