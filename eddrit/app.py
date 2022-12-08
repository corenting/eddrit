import uvicorn
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from eddrit import config
from eddrit.routes.common import exception_handlers
from eddrit.routes.pages import (
    index,
    instance,
    meta,
    over18,
    root_files,
    search,
    settings,
    subreddit,
)
from eddrit.routes.xhr import routes
from eddrit.utils.middlewares import NoReferrerMiddleware

middlewares = [
    Middleware(NoReferrerMiddleware),
]

exceptions_handlers = {
    HTTPException: exception_handlers.http_exception,
    500: exception_handlers.http_exception,  # 500 are handled separately by starlette
}

app = Starlette(
    debug=config.DEBUG,
    routes=[
        Mount("/static", app=StaticFiles(directory="static"), name="static"),
        Mount("/instance", routes=instance.routes),
        Mount("/meta", routes=meta.routes, name="meta"),
        Mount("/r", routes=subreddit.routes, name="subreddit"),
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
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
