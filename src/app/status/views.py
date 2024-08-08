from fastapi import (
    APIRouter,
    Request,
)
from fastapi.responses import Response

from app.core.ksqldb import (
    KsqlEndpoints,
    KsqlException,
    KsqlRequest,
)
from app.core.templates import render_template

router = APIRouter()


@router.get("/status")
async def get_server_status(request: Request) -> Response:
    """View to list all available queries."""
    info = await KsqlRequest(request, endpoint=KsqlEndpoints.INFO, method='GET').execute()
    if not info.is_success:
        raise KsqlException('Failed to get info', info)

    health = await KsqlRequest(request, endpoint=KsqlEndpoints.HEALTH, method='GET').execute()
    if not health.is_success:
        raise KsqlException('Failed to get health', health)

    return render_template('status/index.html', request, info=info.json(), health=health.json())
