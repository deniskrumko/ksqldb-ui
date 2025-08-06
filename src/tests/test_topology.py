import pytest

from app.topology.views import index_view


@pytest.mark.asyncio
async def test_topology_index_view_success(fastapi_request):
    """Test successful topology index view with streams data."""
    response = await index_view(fastapi_request)

    # Verify response is a template response
    assert response.status_code == 200
    assert response.template.name == "topology/index.html"
