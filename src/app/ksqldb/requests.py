from typing import Any

import httpx
from fastapi.requests import Request

from app.helpers.settings import get_server

from .resources import KsqlQuery


class KsqlRequest:
    ACCEPT_HEADER = 'application/vnd.ksql.v1+json'

    def __init__(self, request: Request, raw_query: Any) -> None:
        self._server = get_server(request)
        self._query = KsqlQuery(str(raw_query))

    @property
    def query(self) -> KsqlQuery:
        return self._query

    async def execute(self) -> httpx.Response:
        full_url = self._server / 'ksql'
        async with httpx.AsyncClient() as client:
            return await client.post(
                url=str(full_url),
                json={
                    'ksql': self._query.as_string,
                    'streamsProperties': {},
                },
                headers={
                    'Accept': self.ACCEPT_HEADER,
                },
            )
