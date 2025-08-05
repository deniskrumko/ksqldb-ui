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
