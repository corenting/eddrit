from dataclasses import dataclass
from enum import Enum

from eddrit.models import Flair


@dataclass
class User:
    name: str
    flair: Flair | None

    # only on user pages
    over18: bool = False
    public_description: str = ""

    @property
    def is_deleted(self) -> bool:
        return self.name == "[deleted]"

class UserSortingMode(Enum):
    NEW = "new"
    HOT = "hot"
    TOP = "top"
    CONTROVERSIAL = "controversial"
