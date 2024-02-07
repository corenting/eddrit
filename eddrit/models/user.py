from dataclasses import dataclass
from enum import Enum

from eddrit.models import Flair


@dataclass
class User:
    name: str
    flair: Flair | None

    # only on user pages
    over18: bool = False


class UserSortingMode(Enum):
    NEW = "new"
    HOT = "hot"
    TOP = "top"
    CONTROVERSIAL = "controversial"
