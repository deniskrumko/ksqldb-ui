from fastapi import (
    APIRouter,
    Request,
)
from fastapi.responses import Response

from app.core.ksqldb import (
    KsqlException,
    KsqlRequest,
)
from app.core.templates import (
    httpx_response_to_context,
    render_template,
)

router = APIRouter()


@router.get("/queries")
async def list_view(request: Request) -> Response:
    """View to list all available queries."""
    response = await KsqlRequest(request, 'SHOW QUERIES').execute()
    if not response.is_success:
        raise KsqlException('Failed to show queries', response)

    data = response.json()
    return render_template(
        'queries/list.html',
        request=request,
        queries=data[0]['queries'],
        **httpx_response_to_context(response),
    )
