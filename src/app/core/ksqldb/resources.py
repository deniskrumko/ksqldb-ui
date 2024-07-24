from enum import Enum
from typing import Any


class KsqlEndpoints(Enum):
    KSQL = 'ksql'
    INFO = 'info'
    HEALTH = 'healthcheck'


class KsqlException(Exception):

    def __init__(self, info: str, response: Any) -> None:
        self.info = info
        self.response = response

    def __str__(self) -> str:
        return self.info


class KsqlQuery:

    def __init__(self, data: Any) -> None:
        self._raw_data: Any = data

    def __str__(self) -> str:
        return self.as_string

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {str(self)}>'

    @property
    def raw(self) -> str:
        return str(self._raw_data)

    @property
    def as_string(self) -> str:
        query = ' '.join(v for v in str(self._raw_data).split() if v)

        if not query.endswith(';'):
            query += ';'
        return query
