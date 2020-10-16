from typing import Tuple

from eddrit.const import POST_MAX_CONTENT_HEIGHT, POST_MIN_CONTENT_WIDTH


def get_post_content_size(width: int, height: int) -> Tuple[int, int]:
    max_height_px = POST_MAX_CONTENT_HEIGHT
    min_width_px = POST_MIN_CONTENT_WIDTH

    ret_width = width
    ret_heigth = height

    if height > max_height_px:
        ret_width = int((width * max_height_px) / height)
        ret_heigth = max_height_px

    if width < min_width_px:
        ret_width = min_width_px
        ret_heigth = int((height * min_width_px) / width)

    return ret_width, ret_heigth
