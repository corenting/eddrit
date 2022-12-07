from dataclasses import dataclass
from typing import Optional

from eddrit.models import Flair


@dataclass
class User:
    name: str
    flair: Optional[Flair]
