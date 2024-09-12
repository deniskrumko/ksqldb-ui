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


@router.get("/queries")
async def list_view(request: Request, extra_context: Optional[dict] = None) -> Response:
    """View to list all available queries."""
    response = await KsqlRequest(request, 'SHOW QUERIES').execute()
    if not response.is_success:
        raise KsqlException('Failed to show queries', response)

    data = response.json()
    return render_template(
        'queries/list.html',
        request=request,
        response=response,
        queries=data[0]['queries'],
        **(extra_context or {}),
    )


@router.post('/queries')
async def delete_query(request: Request) -> Response:
    """Route to delete a query."""
    form_data = await request.form()
    query_name = form_data['delete_object']
    if not query_name:
        raise ValueError('Query name is not set')

    response = await KsqlRequest(request, f'TERMINATE {query_name}').execute()
    if not response.is_success:
        raise KsqlException('Failed to drop query', response)

    return await list_view(request, extra_context={
        'deleted_query': query_name,
    })


@router.get('/queries/{query_name}')
async def detail_view(request: Request, query_name: str) -> Response:
    """View to show query details."""
    response = await KsqlRequest(request, f'EXPLAIN {query_name}').execute()
    if not response.is_success:
        raise KsqlException('Failed to explain query', response)

    data = response.json()
    return render_template('queries/details.html', request=request, query=data[0])
