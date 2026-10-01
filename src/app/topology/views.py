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
    queries_response = await ksql.execute_statement("SHOW QUERIES")
    query_status_counts = {}
    if queries_response.status_code == 200:
        query_status_counts = {
            query["id"]: ", ".join(
                f"{status.lower()}: {count}"
                for status, count in query.get("statusCount", {}).items()
            )
            for query in queries_response.json()[0].get("queries", [])
        }

    return render_template(
        "topology/index.html",
        streams=response.json()[0]["sourceDescriptions"],
        response=response,
        query_status_counts=query_status_counts,
        request=request,
    )
