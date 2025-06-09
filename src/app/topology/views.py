from fastapi import (
    APIRouter,
    Request,
)
from fastapi.responses import Response

from app.core.ksqldb import (
    KsqlException,
    KsqlRequest,
)
from app.core.templates import render_template

router = APIRouter()


@router.get("/topology")
async def index_view(request: Request) -> Response:
    """View to list all available queries."""
    response = await KsqlRequest(request, "LIST STREAMS EXTENDED").execute()
    if not response.is_success:
        raise KsqlException("Failed to list streams", response)

    streams_data = response.json()
    return render_template(
        "topology/index.html",
        streams=streams_data[0]["sourceDescriptions"],
        response=response,
        request=request,
    )
