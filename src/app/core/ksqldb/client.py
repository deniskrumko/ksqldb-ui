import json
from abc import (
    ABC,
    abstractmethod,
)
from pathlib import Path
from typing import Any

import httpx
from fastapi.requests import Request

from app.core.i18n import _
from app.core.settings import (
    get_server_code,
    get_settings,
)
from app.core.urls import SimpleURL

from .resources import (
    KsqlEndpoints,
    KsqlErrors,
    KsqlException,
    KsqlQuery,
)

KSQL_CLIENTS_CACHE: dict[str, "AbstractKsqlClient"] = {}


class AbstractKsqlClient(ABC):
    """
    Abstract base class for KSQL clients.
    """

    @abstractmethod
    async def execute_statement(
        self,
        statement: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Execute a KSQL statement (e.g., CREATE STREAM) and return the result."""

    @abstractmethod
    async def execute_query(
        self,
        query: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Execute a KSQL query and return the result."""

    @abstractmethod
    async def execute_statement_then_query(
        self,
        statement_or_query: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Execute a KSQL statement then fallback to query."""

    @abstractmethod
    async def get_info(self, **kwargs: Any) -> httpx.Response:
        """Get server info."""

    @abstractmethod
    async def get_health(self, **kwargs: Any) -> httpx.Response:
        """Get server health."""


class KsqlClient(AbstractKsqlClient):

    ACCEPT_HEADER = "application/vnd.ksql.v1+json"

    def __init__(
        self,
        url: str,
        timeout: int = 10,
    ) -> None:
        """Initialize class instance."""
        self.url = SimpleURL(url)
        self.timeout = timeout

    async def execute_statement(
        self,
        statement: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Execute a KSQL statement."""
        return await self._request(
            query=KsqlQuery(statement),
            method="POST",
            endpoint=KsqlEndpoints.KSQL,
            **kwargs,
        )

    async def execute_query(
        self,
        query: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Execute a KSQL query."""
        return await self._request(
            query=KsqlQuery(query),
            method="POST",
            endpoint=KsqlEndpoints.QUERY,
            **kwargs,
        )

    async def execute_statement_then_query(
        self,
        statement_or_query: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Execute a KSQL statement then fallback to query."""
        statement_response = await self.execute_statement(
            statement_or_query,
            raise_exc=False,
            **kwargs,
        )

        if (
            statement_response.status_code == 400
            and statement_response.json()["error_code"] == KsqlErrors.QUERY_ENDPOINT.value
        ):
            return await self.execute_query(statement_or_query, **kwargs)

        return statement_response

    async def get_info(self, **kwargs: Any) -> httpx.Response:
        """Get server info."""
        return await self._request(
            query=KsqlQuery(""),
            method="GET",
            endpoint=KsqlEndpoints.INFO,
            **kwargs,
        )

    async def get_health(self, **kwargs: Any) -> httpx.Response:
        """Get server health."""
        return await self._request(
            query=KsqlQuery(""),
            method="GET",
            endpoint=KsqlEndpoints.HEALTH,
            **kwargs,
        )

    async def _request(
        self,
        query: KsqlQuery,
        method: str,
        endpoint: KsqlEndpoints,
        raise_exc: bool = True,
        exc_message: str | None = None,
        list_page_url: str | None = None,
    ) -> httpx.Response:
        """Get response from endpoint"""
        full_url = self.url / endpoint.value
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=str(full_url),
                json={
                    "ksql": query.as_string,
                    # TODO: Add custom streamsProperties
                    "streamsProperties": {},
                },
                headers={
                    "Accept": self.ACCEPT_HEADER,
                },
                timeout=self.timeout,
            )

            if raise_exc and not response.is_success:
                raise KsqlException(
                    info=exc_message or _("Failed to execute ksqlDB request: {}").format(query),
                    response=response,
                    list_page_url=list_page_url,
                )

            return response


class MockKsqlClient(KsqlClient):
    """Mock class for KSQL requests to simulate responses."""

    RESPONSES_MAP = {
        KsqlEndpoints.QUERY: {},
        KsqlEndpoints.INFO: {"": "info.json"},
        KsqlEndpoints.HEALTH: {"": "health.json"},
        KsqlEndpoints.KSQL: {
            "LIST STREAMS EXTENDED;": "list_streams_extended.json",
            "SHOW PROPERTIES;": "show_properties.json",
        },
    }

    def __init__(self) -> None:
        """Initialize class instance."""
        self.url = SimpleURL("http://localhost.test")
        self.response_dir = Path(__file__).parent / "responses"

    async def _request(
        self,
        query: KsqlQuery,
        method: str,
        endpoint: KsqlEndpoints,
        raise_exc: bool = True,
        exc_message: str | None = None,
        list_page_url: str | None = None,
    ) -> httpx.Response:
        """Get response from endpoint"""
        file_name = self.RESPONSES_MAP[endpoint].get(query.as_string)
        if not file_name:
            raise ValueError(f'No mocked response for {endpoint} query: "{query}"')

        with open(self.response_dir / file_name, "r") as f:
            mock_response_data = json.load(f)

        full_url = self.url / endpoint.value
        return httpx.Response(
            status_code=200,
            json=mock_response_data,
            request=httpx.Request(method, str(full_url)),
        )


def get_ksql_client(request: Request) -> AbstractKsqlClient:
    """Get KsqlDB client depending on scope."""
    if request.scope.get("test", False):
        return MockKsqlClient()

    code = get_server_code(request)
    if code in KSQL_CLIENTS_CACHE:
        return KSQL_CLIENTS_CACHE[code]

    settings = get_settings()
    server = settings.get_server(code)

    new_client = KsqlClient(
        url=server.url,
        timeout=settings.http.timeout,
    )

    KSQL_CLIENTS_CACHE[code] = new_client
    return new_client
