from collections.abc import Hashable
from typing import Any

from eddrit import models


def get_post_flair(api_post_data: dict[Hashable, Any]) -> models.Flair | None:
    flair_components = []

    # Colors
    text_color = (
        "black" if api_post_data["link_flair_text_color"] == "dark" else "white"
    )

    if (
        api_post_data["link_flair_background_color"]
        and api_post_data["link_flair_background_color"] != "transparent"
    ):
        bg_color = api_post_data["link_flair_background_color"]

        # Reset the text color to black if we have a white background
        if bg_color == "#ffffff" and text_color == "white":
            text_color = "#000000"
    else:
        bg_color = "lightblue"

    if api_post_data.get("is_original_content", False):
        flair_components.append(
            models.FlairComponent(content="OC", type=models.FlairComponentType.TEXT)
        )

    if api_post_data.get("link_flair_richtext"):
        for part in api_post_data.get("link_flair_richtext", []):
            part_type = part["e"]

            if part_type == "text":
                flair_components.append(
                    models.FlairComponent(
                        content=part["t"], type=models.FlairComponentType.TEXT
                    )
                )
            elif part_type == "emoji":
                flair_components.append(
                    models.FlairComponent(
                        content=part["u"], type=models.FlairComponentType.EMOJI
                    )
                )

    elif api_post_data.get("link_flair_text"):
        flair_components.append(
            models.FlairComponent(
                content=api_post_data["link_flair_text"],
                type=models.FlairComponentType.TEXT,
            )
        )

    if len(flair_components) != 0:
        return models.Flair(
            background_color=bg_color,
            text_color=text_color,
            components=flair_components,
        )
    return None


def get_user_flair(api_post_data: dict[Hashable, Any]) -> models.Flair | None:
    flair_components = []

    # Background color
    if (
        api_post_data["author_flair_background_color"]
        and api_post_data["author_flair_background_color"] != "transparent"
    ):
        bg_color = api_post_data["author_flair_background_color"]
    else:
        bg_color = "lightblue"

    # Text color
    text_color = (
        "black" if api_post_data["author_flair_text_color"] == "dark" else "white"
    )

    if api_post_data.get("author_flair_richtext"):
        for part in api_post_data.get("author_flair_richtext", []):
            part_type = part["e"]

            if part_type == "text":
                flair_components.append(
                    models.FlairComponent(
                        content=part["t"], type=models.FlairComponentType.TEXT
                    )
                )
            elif part_type == "emoji":
                flair_components.append(
                    models.FlairComponent(
                        content=part["u"], type=models.FlairComponentType.EMOJI
                    )
                )

    elif api_post_data.get("author_flair_text"):
        flair_components.append(
            models.FlairComponent(
                content=api_post_data["author_flair_text"],
                type=models.FlairComponentType.TEXT,
            )
        )

    if len(flair_components) != 0:
        return models.Flair(
            background_color=bg_color,
            text_color=text_color,
            components=flair_components,
        )

    return None
