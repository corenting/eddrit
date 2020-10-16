from dataclasses import dataclass
from enum import Enum
from typing import List


class FlairType(Enum):
    EMOJI = "emoji"
    TEXT = "text"


@dataclass
class FlairItem:
    content: str
    item_type: FlairType


@dataclass
class Flair:
    background_color: str
    text_color: str
    items: List[FlairItem]
