from pathlib import Path

from fastapi import (
    FastAPI,
    Request,
)
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse

from .ksqldb import (
    Query,
    make_request,
)

app = FastAPI()
templates_dir = Path(__file__).parent.parent / 'templates'
templates = Jinja2Templates(directory=templates_dir)


@app.get("/")
async def index_get(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(
        'index.html',
        context={'request': request},
    )


@app.post('/')
async def index_post(request: Request) -> _TemplateResponse:
    form_data = await request.form()
    query = Query(data=form_data['query'])
    server = 'http://0.0.0.0:8088'
    response = await make_request(server, query)
    return templates.TemplateResponse(
        'index.html',
        context={
            'request': request,
            'ksqldb_request': response.request,
            'ksqldb_response': response,
            'query': query,
        },
    )
