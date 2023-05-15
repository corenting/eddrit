from dataclasses import asdict, is_dataclass
import json
from typing import Any


def tojson_dataclass(value: Any) -> str:
    """tojson filter compatible with dataclasses."""
    return json.dumps(asdict(value) if is_dataclass(value) else value, default=str)
