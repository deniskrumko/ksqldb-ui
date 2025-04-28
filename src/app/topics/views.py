from typing import Optional

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


@router.get("/topics")
async def list_view(request: Request, extra_context: Optional[dict] = None) -> Response:
    """View to list all available queries."""
    response = await KsqlRequest(request, "SHOW TOPICS EXTENDED").execute()
    if not response.is_success:
        raise KsqlException("Failed to show topics", response)

    data = response.json()
    return render_template(
        "topics/list.html",
        request=request,
        response=response,
        topics=data[0]["topics"],
        **(extra_context or {}),
    )
