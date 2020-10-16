from typing import Any

from eddrit import models


def get_settings_from_request(request: Any) -> models.Settings:
    return models.Settings(
        nsfw_popular_all=request.cookies.get("nsfw_popular_all", "0") == "1",
        nsfw_thumbnails=request.cookies.get("nsfw_thumbnails", "0") == "1",
    )
