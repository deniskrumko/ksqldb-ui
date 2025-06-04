from typing import (
    Any,
    Optional,
)

import httpx
from fastapi.requests import Request

from app.core.settings import (
    get_server,
    get_settings,
)
from app.core.urls import SimpleURL

from .resources import (
    KsqlEndpoints,
    KsqlErrors,
    KsqlQuery,
)


class KsqlRequest:
    """Base class for requests to KSQL server."""

    ACCEPT_HEADER = "application/vnd.ksql.v1+json"

    def __init__(
        self,
        request: Request,
        raw_query: Optional[Any] = None,
        endpoint: KsqlEndpoints = KsqlEndpoints.KSQL,
        method: str = "POST",
        timeout: Optional[int] = None,
    ) -> None:
        """Initialize class instance."""
        self._server: SimpleURL = get_server(request).simple_url
        self._query = KsqlQuery(str(raw_query))
        self._endpoint = endpoint
        self._method = method
        self._timeout = timeout or get_settings().http.timeout

    @property
    def query(self) -> KsqlQuery:
        """Get KSQL query."""
        return self._query

    async def execute(self, query_fallback: bool = False) -> httpx.Response:
        """Execute KSQL request to default endpoint."""
        response = await self._request(self._endpoint)

        # If with_fallback enabled, then try request to /query endpoint
        if (
            query_fallback
            and response.status_code == 400
            and response.json()["error_code"] == KsqlErrors.QUERY_ENDPOINT.value
        ):
            return await self._request(KsqlEndpoints.QUERY)

        return response

    async def _request(self, endpoint: KsqlEndpoints) -> httpx.Response:
        """Get response from endpoint"""
        full_url = self._server / endpoint.value
        async with httpx.AsyncClient() as client:
            return await client.request(
                method=self._method,
                url=str(full_url),
                json={
                    "ksql": self._query.as_string,
                    # TODO: Add custom streamsProperties
                    "streamsProperties": {},
                },
                headers={
                    "Accept": self.ACCEPT_HEADER,
                },
                timeout=self._timeout,
            )
