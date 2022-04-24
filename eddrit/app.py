import uvicorn
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from eddrit import config
from eddrit.config import PROXY_ENABLED
from eddrit.routes import (
    api,
    index,
    instance,
    meta,
    over18,
    root_files,
    settings,
    subreddit,
)
from eddrit.routes.common import exception_handlers
from eddrit.utils.middlewares import NoReferrerMiddleware, ProxyHeadersMiddleware

middlewares = [
    Middleware(NoReferrerMiddleware),
]
if PROXY_ENABLED:
    middlewares.insert(0, Middleware(ProxyHeadersMiddleware))

exceptions_handlers = {HTTPException: exception_handlers.http_exception}

app = Starlette(
    debug=config.DEBUG,
    routes=[
        Mount("/static", app=StaticFiles(directory="static"), name="static"),
        Mount("/instance", routes=instance.routes),
        Mount("/meta", routes=meta.routes, name="meta"),
        Mount("/r", routes=subreddit.routes, name="subreddit"),
        Mount("/api", routes=api.routes, name="api"),
        Mount(
            "/",
            routes=[
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
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
