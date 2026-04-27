from dataclasses import dataclass


@dataclass
class Link:
    name: str
    target: str
    is_javascript_target: bool
    html_id: str | None = None
    html_data: str | None = None
