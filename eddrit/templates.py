from importlib.metadata import version

from starlette.templating import Jinja2Templates

from eddrit.utils.subreddit import is_homepage

templates = Jinja2Templates(directory="templates")

# Add global informations to env
templates.env.globals["global"] = {
    "app_version": version("eddrit"),
    "subreddit_is_homepage": is_homepage,
}
