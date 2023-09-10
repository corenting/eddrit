from dataclasses import dataclass
from enum import Enum


class ThumbnailsMode(Enum):
    ALWAYS = "always"
    NEVER = "never"
    SUBREDDIT_PREFERENCE = "subreddit_preference"


@dataclass
class Settings:
    thumbnails: ThumbnailsMode
    nsfw_popular_all: bool
    nsfw_thumbnails: bool
