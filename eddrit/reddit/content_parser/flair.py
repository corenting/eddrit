from typing import Any, Dict, Hashable, Optional

from eddrit import models


def get_post_flair(api_post_data: Dict[Hashable, Any]) -> Optional[models.Flair]:
    flair_items = []

    # Background color
    bg_color = api_post_data["link_flair_background_color"]
    if not bg_color or bg_color == "#ffffff":
        bg_color = "#6495ED"

    # Text color
    text_color = api_post_data["link_flair_text_color"]
    if not text_color:
        text_color = "#ffffff"

    if api_post_data.get("is_original_content", False):
        flair_items.append(
            models.FlairItem(content="OC", item_type=models.FlairType.TEXT)
        )

    if api_post_data.get("link_flair_richtext"):
        for part in api_post_data.get("link_flair_richtext", []):
            part_type = part["e"]

            if part_type == "text":
                flair_items.append(
                    models.FlairItem(content=part["t"], item_type=models.FlairType.TEXT)
                )
            elif part_type == "emoji":
                flair_items.append(
                    models.FlairItem(
                        content=part["u"], item_type=models.FlairType.EMOJI
                    )
                )

    elif api_post_data.get("link_flair_text"):
        flair_items.append(
            models.FlairItem(
                content=api_post_data["link_flair_text"],
                item_type=models.FlairType.TEXT,
            )
        )

    if len(flair_items) != 0:
        return models.Flair(
            background_color=bg_color,
            text_color=text_color,
            items=flair_items,
        )
    return None


def get_user_flair(api_post_data: Dict[Hashable, Any]) -> Optional[models.Flair]:
    flair_items = []

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
                flair_items.append(
                    models.FlairItem(content=part["t"], item_type=models.FlairType.TEXT)
                )
            elif part_type == "emoji":
                flair_items.append(
                    models.FlairItem(
                        content=part["u"], item_type=models.FlairType.EMOJI
                    )
                )

    elif api_post_data.get("author_flair_text"):
        flair_items.append(
            models.FlairItem(
                content=api_post_data["author_flair_text"],
                item_type=models.FlairType.TEXT,
            )
        )

    if len(flair_items) != 0:
        return models.Flair(
            background_color=bg_color,
            text_color=text_color,
            items=flair_items,
        )

    return None
