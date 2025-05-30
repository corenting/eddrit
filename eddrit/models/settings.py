from dataclasses import dataclass
from enum import Enum


class ThumbnailsMode(Enum):
    ALWAYS = "always"
    NEVER = "never"
    SUBREDDIT_PREFERENCE = "subreddit_preference"


class LayoutMode(Enum):
    WIDE = "wide"
    COMPACT = "compact"


class Theme(Enum):
    SYSTEM = ""  # unset
    LIGHT = "light"
    DARK = "dark"


@dataclass
class Settings:
    layout: LayoutMode
    thumbnails: ThumbnailsMode
    nsfw_popular_all: bool
    nsfw_thumbnails: bool
    theme: Theme
