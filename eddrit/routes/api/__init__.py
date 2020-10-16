from starlette.routing import Mount

from eddrit.routes.api.comments import routes as comments_routes

routes = [
    Mount("/comments", routes=comments_routes),
]
