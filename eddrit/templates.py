from starlette.templating import Jinja2Templates

from eddrit import __version__, models
from eddrit.utils.jinja import tojson_dataclass
from eddrit.utils.subreddit import is_homepage

templates = Jinja2Templates(directory="templates")

# Add global informations to env
templates.env.globals["global"] = {
    "app_version": __version__,
    "subreddit_is_homepage": is_homepage,
    "sorting_modes": [e.value for e in models.SubredditSortingMode],
    "sorting_periods": [e.value for e in models.SubredditSortingPeriod],
}
templates.env.filters["tojson_dataclass"] = tojson_dataclass
