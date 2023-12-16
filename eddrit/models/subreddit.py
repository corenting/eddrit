from dataclasses import dataclass
from enum import Enum


@dataclass
class Subreddit:
    title: str
    name: str
    show_thumbnails: bool
    public_description: str | None
    over18: bool
    icon_url: str | None


class SubredditSortingMode(Enum):
    POPULAR = "popular"
    NEW = "new"
    RISING = "rising"
    CONTROVERSIAL = "controversial"
    TOP = "top"
    GILDED = "gilded"


class SubredditSortingPeriod(Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"
