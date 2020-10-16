from dataclasses import dataclass
from typing import Optional


@dataclass
class Pagination:
    before_post_id: Optional[str]
    after_post_id: Optional[str]
