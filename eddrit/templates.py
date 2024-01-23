import json
from dataclasses import asdict, is_dataclass

from starlette.templating import Jinja2Templates

from eddrit import __version__, models
from eddrit.utils.subreddit import is_homepage

templates = Jinja2Templates(directory="templates")

# Add global information to env
templates.env.globals["global"] = {
    "app_version": __version__,
    "subreddit_is_homepage": is_homepage,
    "sorting_modes": [e.value for e in models.SubredditSortingMode],
    "sorting_periods": [e.value for e in models.SubredditSortingPeriod],
}

# Add a json filter compatible with dataclasses
templates.env.filters["tojson_dataclass"] = lambda value: json.dumps(
    asdict(value) if is_dataclass(value) else value, default=str
)
