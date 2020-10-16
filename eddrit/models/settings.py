from dataclasses import dataclass


@dataclass
class Settings:
    nsfw_popular_all: bool = False
    nsfw_thumbnails: bool = False
