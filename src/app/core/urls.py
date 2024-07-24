class SimpleURL:
    def __init__(self, url: str) -> None:
        self._url = url

    def __str__(self) -> str:
        return self._url

    def __truediv__(self, other: str) -> 'SimpleURL':
        base = self._url.rstrip('/')
        new_part = other.lstrip('/')
        return SimpleURL(f'{base}/{new_part}')
