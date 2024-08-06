from enum import Enum
from typing import Any


class KsqlEndpoints(Enum):
    """Enum with all available KSQL endpoints."""

    KSQL = 'ksql'
    INFO = 'info'
    HEALTH = 'healthcheck'


class KsqlException(Exception):
    """Base class for KSQL exceptions."""

    def __init__(self, info: str, response: Any) -> None:
        """Initialize class instance."""
        self.info = info
        self.response = response

    def __str__(self) -> str:
        """Return string representation."""
        return self.info


class KsqlQuery:
    """Representation of KSQL query."""

    def __init__(self, data: Any) -> None:
        """Initialize class instance."""
        self._raw_data: Any = data

    def __str__(self) -> str:
        """Return string representation."""
        return self.as_string

    def __repr__(self) -> str:
        """Return object representation."""
        return f'<{self.__class__.__name__}: {str(self)}>'

    @property
    def raw(self) -> str:
        """Get raw query data."""
        return str(self._raw_data)

    @property
    def as_string(self) -> str:
        """Get KSQL query as string."""
        query = ' '.join(v for v in str(self._raw_data).split() if v)

        if not query.endswith(';'):
            query += ';'
        return query
