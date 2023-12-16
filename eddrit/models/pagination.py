from dataclasses import dataclass


@dataclass
class Pagination:
    before_post_id: str | None
    after_post_id: str | None
