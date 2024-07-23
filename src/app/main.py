import traceback
from pathlib import Path
from typing import (
    Any,
    Callable,
)

from fastapi import (
    FastAPI,
    Request,
)
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from .helpers.settings import get_settings
from .helpers.templates import (
    TemplateResponse,
    render_template,
)
from .helpers.utils import make_list
from .ksqldb.resources import KsqlException
from .routes import ALL_ROUTES

app = FastAPI()
app.settings = get_settings()

static_dir = Path(__file__).parent.parent / 'static'
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Registering routes in app
for router in ALL_ROUTES:
    app.include_router(router)


@app.middleware("http")
async def add_default_server(request: Request, call_next: Callable) -> Any:
    if (
        request.method == 'GET'
        and ('/static/' not in str(request.url))
        and not request.query_params.get('s')
    ):
        default_server = list(app.settings['servers'].keys())[0]
        return RedirectResponse(f'?s={default_server}')

    return await call_next(request)


@app.exception_handler(400)
@app.exception_handler(404)
@app.exception_handler(500)
async def http_exception_handler(request: Request, exc: Exception) -> TemplateResponse:
    params: dict = {
        'exception': exc.__class__.__name__,
        'detail': str(exc),
        'tb': traceback.format_exception(exc.__class__, exc, exc.__traceback__),
    }

    if isinstance(exc, KsqlException):
        try:
            response_data = make_list(exc.response.json())
        except Exception:
            response_data = None

        params['detail'] = exc.info
        params['response_data'] = response_data
        params['response_code'] = exc.response.status_code

    return render_template('error.html', request=request, **params)
