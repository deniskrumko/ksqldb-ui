from fastapi import (
    APIRouter,
    Request,
)
from starlette.responses import Response

from app.helpers.templates import render_template
from app.helpers.utils import make_list
from app.ksqldb import KsqlRequest

router = APIRouter()


@router.get("/requests")
async def show_request_editor(request: Request) -> Response:
    """View to show request editor."""
    return render_template('requests/index.html', request)


@router.post('/requests')
async def perform_request(request: Request) -> Response:
    """Perform request to ksqlDB server."""
    form_data = await request.form()
    ksql_request = KsqlRequest(request, form_data['query'])
    ksql_response = await ksql_request.execute()

    response_code = ksql_response.status_code
    response_data = make_list(ksql_response.json())
    return render_template(
        'requests/index.html',
        request=request,
        query=ksql_request.query,
        response_code=response_code,
        response_data=response_data,
    )
