from typing import Any


class SimpleURL:
    """Class for URLs.

    Mimics pathlib.Path class:

    >>> SimpleURL('https://example.com') / 'path'
    https://example.com/path
    """

    def __init__(self, url: str) -> None:
        """Initialize class instance."""
        self._url = url

    def __str__(self) -> str:
        """Return string representation."""
        return self._url

    def __truediv__(self, other: str) -> 'SimpleURL':
        """Return new SimpleURL object."""
        base = self._url.rstrip('/')
        new_part = other.strip('/')
        return SimpleURL(f'{base}/{new_part}')

    def __eq__(self, value: Any) -> bool:
        """Return True if value is equal to self."""
        if not isinstance(value, SimpleURL):
            raise TypeError('can only compare to other SimpleURL objects')

        return self._url == value._url
