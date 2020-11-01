import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from eddrit import config
from eddrit.config import PROXY_ENABLED
from eddrit.routes import api, index, instance, meta, over18, settings, subreddit
from eddrit.utils.middlewares import NoReferrerMiddleware, ProxyHeadersMiddleware

middlewares = [
    Middleware(NoReferrerMiddleware),
]
if PROXY_ENABLED:
    middlewares.insert(0, Middleware(ProxyHeadersMiddleware))

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
            routes=[*index.routes, *over18.routes, *settings.routes],
            name="root",
        ),
    ],
    middleware=middlewares,
)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
