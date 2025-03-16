import json
from dataclasses import asdict, is_dataclass
from typing import Any

from starlette.templating import Jinja2Templates

from eddrit import __version__, models
from eddrit.utils.subreddit import is_homepage

templates = Jinja2Templates(directory="templates")

# Add global information to env
templates.env.globals["global"] = {
    "app_version": __version__,
    "subreddit_is_homepage": is_homepage,
    "subreddit_sorting_modes": [e.value for e in models.SubredditSortingMode],
    "user_sorting_modes": [e.value for e in models.UserSortingMode],
    "sorting_periods": [e.value for e in models.SubredditSortingPeriod],
}


# Add a json filter compatible with dataclasses
def to_json_dataclass(value: Any) -> str:
    if type(value) is list:
        converted = [asdict(item) if is_dataclass(item) else item for item in value]  # type: ignore
    else:
        converted = asdict(value) if is_dataclass(value) else value  # type: ignore
    return json.dumps(converted, default=str)


templates.env.filters["tojson_dataclass"] = to_json_dataclass
