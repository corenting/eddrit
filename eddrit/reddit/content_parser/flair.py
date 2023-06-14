from typing import Any, Dict, Hashable, Optional

from eddrit import models


def get_post_flair(api_post_data: Dict[Hashable, Any]) -> Optional[models.Flair]:
    flair_components = []

    # Colors
    text_color = (
        "black" if api_post_data["link_flair_text_color"] == "dark" else "white"
    )
    bg_color = api_post_data["link_flair_background_color"]

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


def get_user_flair(api_post_data: Dict[Hashable, Any]) -> Optional[models.Flair]:
    flair_components = []

    # Background color
    bg_color = api_post_data["author_flair_background_color"]
    if not bg_color or bg_color == "#ffffff":
        bg_color = "#dadada"

    # Text color
    text_color = api_post_data["author_flair_text_color"]
    if not text_color:
        text_color = "#0000"

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
