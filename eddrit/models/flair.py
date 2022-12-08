from dataclasses import dataclass
from enum import Enum
from typing import List


class FlairComponentType(Enum):
    EMOJI = "emoji"
    TEXT = "text"


@dataclass
class FlairComponent:
    content: str
    type: FlairComponentType


@dataclass
class Flair:
    background_color: str
    text_color: str
    components: List[FlairComponent]
