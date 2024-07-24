from typing import (
    Any,
    Optional,
)

import httpx
from fastapi.requests import Request

from app.core.settings import get_server_url
from app.core.urls import SimpleURL

from .resources import (
    KsqlEndpoints,
    KsqlQuery,
)


class KsqlRequest:
    ACCEPT_HEADER = 'application/vnd.ksql.v1+json'

    def __init__(
        self,
        request: Request,
        raw_query: Optional[Any] = None,
        endpoint: KsqlEndpoints = KsqlEndpoints.KSQL,
        method: str = 'POST',
    ) -> None:
        self._server: SimpleURL = get_server_url(request)
        self._query = KsqlQuery(str(raw_query))
        self._endpoint = endpoint
        self._method = method

    @property
    def query(self) -> KsqlQuery:
        return self._query

    async def execute(self) -> httpx.Response:
        full_url = self._server / self._endpoint.value
        async with httpx.AsyncClient() as client:
            return await client.request(
                method=self._method,
                url=str(full_url),
                json={
                    'ksql': self._query.as_string,
                    'streamsProperties': {},
                },
                headers={
                    'Accept': self.ACCEPT_HEADER,
                },
            )
