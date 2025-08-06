from fastapi import (
    APIRouter,
    Request,
)
from fastapi.responses import Response

from app.core.ksqldb import get_ksql_client
from app.core.templates import render_template

router = APIRouter()


@router.get("/topology")
async def index_view(request: Request) -> Response:
    """View to list all available queries."""
    ksql = get_ksql_client(request)
    response = await ksql.execute_statement("LIST STREAMS EXTENDED")

    return render_template(
        "topology/index.html",
        streams=response.json()[0]["sourceDescriptions"],
        response=response,
        request=request,
    )
