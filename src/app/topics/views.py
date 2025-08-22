from typing import Optional

from fastapi import (
    APIRouter,
    Request,
)
from fastapi.responses import Response

from app.core.ksqldb import get_ksql_client
from app.core.templates import render_template

router = APIRouter()


@router.get("/topics")
async def list_view(request: Request, extra_context: Optional[dict] = None) -> Response:
    """View to list all available queries."""
    response = await get_ksql_client(request).execute_statement("SHOW TOPICS EXTENDED")
    return render_template(
        "topics/list.html",
        request=request,
        response=response,
        topics=sorted(response.json()[0]["topics"], key=lambda x: x["name"].lower()),
        **(extra_context or {}),
    )


@router.get("/topics/{topic_name}")
async def detail_view(request: Request, topic_name: str) -> Response:
    """View to show topic details."""
    response = await get_ksql_client(request).execute_statement("LIST STREAMS")

    data = response.json()
    query = data[0]
    streams = sorted(
        [s for s in query["streams"] if s["topic"] == topic_name],
        key=lambda x: x["name"].lower(),
    )

    return render_template(
        "topics/details.html",
        request=request,
        response=response,
        topic_name=topic_name,
        streams=streams,
    )
