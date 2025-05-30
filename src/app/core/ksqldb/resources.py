from enum import Enum
from typing import Any

COMMENT_PREFIX = "--"
KSQL_SYSTEM_STREAM = "KSQL_PROCESSING_LOG"


class KsqlEndpoints(Enum):
    """Enum with all available KSQL endpoints."""

    KSQL = "ksql"
    QUERY = "query"
    INFO = "info"
    HEALTH = "healthcheck"


class KsqlErrors(Enum):
    """Enum with all available KSQL errors."""

    BAD_STATEMENT = 40001
    QUERY_ENDPOINT = 40002


class KsqlException(Exception):
    """Base class for KSQL exceptions."""

    def __init__(
        self,
        info: str,
        response: Any,
        list_page_url: str | None = None,
    ) -> None:
        """Initialize class instance."""
        self.info = info
        self.response = response
        self.list_page_url = list_page_url

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
        return f"<{self.__class__.__name__}: {str(self)}>"

    @property
    def raw(self) -> str:
        """Get raw query data."""
        return str(self._raw_data)

    @property
    def as_string(self) -> str:
        """Get KSQL query as string."""
        query = " ".join(
            line.strip()
            for line in str(self._raw_data).splitlines()
            if line and not line.startswith(COMMENT_PREFIX)
        )

        if not query.endswith(";"):
            query += ";"
        return query
