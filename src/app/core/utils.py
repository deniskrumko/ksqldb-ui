from typing import Any


def make_list(value: Any) -> list:
    """Convert value to list if not already."""
    return [value] if not isinstance(value, list) else value
