from fastapi import (
    APIRouter,
    Request,
)
from fastapi.responses import (
    RedirectResponse,
    Response,
)

from app.helpers.templates import render_template
from app.ksqldb import (
    KsqlException,
    KsqlRequest,
)

router = APIRouter()


@router.get("/streams")
async def list_view(request: Request) -> Response:
    """View to list all available streams."""
    response = await KsqlRequest(request, 'SHOW STREAMS').execute()
    if not response.is_success:
        raise KsqlException('Failed to show streams', response)

    data = response.json()
    return render_template('streams/list.html', request, streams=data[0]['streams'])


@router.get('/streams/{stream_name}')
async def detail_view(request: Request, stream_name: str) -> Response:
    """View to show stream details."""
    response = await KsqlRequest(request, f'DESCRIBE {stream_name}').execute()
    if not response.is_success:
        raise KsqlException('Failed to describe stream', response)

    data = response.json()
    return render_template('streams/details.html', request=request, stream=data[0])


@router.get('/streams/{stream_name}/delete', response_class=RedirectResponse)
async def delete_stream(request: Request, stream_name: str) -> str:
    """Route to delete a stream."""
    response = await KsqlRequest(request, f'DROP STREAM {stream_name}').execute()
    if not response.is_success:
        raise KsqlException('Failed to drop stream', response)

    return '/streams'
