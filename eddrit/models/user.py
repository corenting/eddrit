from dataclasses import dataclass

from eddrit.models import Flair


@dataclass
class User:
    name: str
    flair: Flair
