import pytest

from app.status.views import (
    debug_view,
    server_status_view,
)
from app.topology.views import index_view


@pytest.mark.asyncio
async def test_topology_index_view_success(fastapi_request):
    """Test successful topology index view with streams data."""
    response = await index_view(fastapi_request)

    # Verify response is a template response
    assert response.status_code == 200
    assert response.template.name == "topology/index.html"


@pytest.mark.asyncio
async def test_status_view_success(fastapi_request):
    """Test successful status view with mocked ksqlDB client."""
    response = await server_status_view(fastapi_request)

    # Verify response is a template response
    assert response.status_code == 200
    assert response.template.name == "status/index.html"
    assert "info" in response.context
    assert "health" in response.context
    assert "properties" in response.context


@pytest.mark.asyncio
async def test_debug_view_success(fastapi_request):
    """Test successful debug view with mocked ksqlDB client."""
    response = await debug_view(fastapi_request)

    # Verify response is a template response
    assert response.status_code == 200
    assert response.template.name == "status/debug.html"
