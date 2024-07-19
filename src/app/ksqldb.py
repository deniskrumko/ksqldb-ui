from typing import Any
from urllib.parse import urljoin

import httpx


class Query:

    def __init__(self, data: Any) -> None:
        self._raw_data: Any = data

    def __str__(self) -> str:
        return self.as_string

    def __repr__(self) -> str:
        return f'<Query: {str(self)}>'

    @property
    def raw(self) -> Any:
        return self._raw_data

    @property
    def as_string(self) -> str:
        query = ''.join(str(self._raw_data).splitlines())

        if not query.endswith(';'):
            query += ';'
        return query


async def make_request(server: str, query: Query) -> httpx.Response:
    full_url = urljoin(server, 'ksql')

    async with httpx.AsyncClient() as client:
        headers = {'Accept': 'application/vnd.ksql.v1+json'}
        return await client.post(
            url=full_url,
            json={"ksql": query.as_string},
            headers=headers,
        )
