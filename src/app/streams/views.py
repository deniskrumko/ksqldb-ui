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
from app.core.templates import (
    httpx_response_to_context,
    render_template,
)

router = APIRouter()


@router.get("/streams")
async def list_view(request: Request, extra_context: Optional[dict] = None) -> Response:
    """View to list all available streams."""
    response = await KsqlRequest(request, 'SHOW STREAMS').execute()
    if not response.is_success:
        raise KsqlException('Failed to show streams', response)

    data = response.json()
    return render_template(
        'streams/list.html',
        request=request,
        streams=data[0]['streams'],
        **httpx_response_to_context(response),
        **(extra_context or {}),
    )


@router.post('/streams')
async def delete_stream(request: Request) -> Response:
    """Route to delete a stream."""
    form_data = await request.form()
    stream_name = form_data['stream_name']
    if not stream_name:
        raise ValueError('Stream name is not set')

    response = await KsqlRequest(request, f'DROP STREAM {stream_name}').execute()
    if not response.is_success:
        raise KsqlException('Failed to drop stream', response)

    return await list_view(request, extra_context={
        'deleted_stream': stream_name,
    })


@router.get('/streams/{stream_name}')
async def detail_view(request: Request, stream_name: str) -> Response:
    """View to show stream details."""
    response = await KsqlRequest(request, f'DESCRIBE {stream_name}').execute()
    if not response.is_success:
        raise KsqlException('Failed to describe stream', response)

    data = response.json()
    return render_template('streams/details.html', request=request, stream=data[0])
