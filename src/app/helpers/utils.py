from typing import Any


def make_list(value: Any) -> list:
    return [value] if not isinstance(value, list) else value
