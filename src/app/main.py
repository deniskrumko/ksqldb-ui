import traceback
from typing import (
    Any,
    Callable,
)

import httpx
from fastapi import (
    Request,
    Response,
)
from starlette.responses import RedirectResponse

from app.core.fastapi import init_fastapi_app
from app.core.ksqldb import KsqlException
from app.core.settings import (
    Server,
    get_server_code,
)
from app.core.templates import (
    ERROR_TEMPLATE,
    render_template,
    run_startup_checks,
)
from app.core.utils import make_list

# Initialize FastAPI application
app = init_fastapi_app()


@app.middleware("http")
async def add_default_server(request: Request, call_next: Callable) -> Any:
    """Add default server from settings if not set."""
    if (
        request.method == "GET"
        and ("/static/" not in str(request.url))
        and not get_server_code(request, raise_exc=False)
    ):
        server: Server = app.settings.default_server
        return RedirectResponse(f"?{server.query}")

    return await call_next(request)


@app.exception_handler(400)
@app.exception_handler(404)
@app.exception_handler(500)
async def http_exception_handler(request: Request, exc: Exception) -> Response:
    params: dict = {
        "exception": exc.__class__.__name__,
        "detail": str(exc),
        "tb": traceback.format_exception(exc.__class__, exc, exc.__traceback__),
    }

    if isinstance(exc, KsqlException):
        try:
            response_data = make_list(exc.response.json())
        except Exception:
            response_data = None

        params["detail"] = exc.info
        params["error_response"] = {
            "data": response_data,
            "code": exc.response.status_code,
        }
        params["list_page_url"] = exc.list_page_url

    if isinstance(exc, httpx.ReadError) and not str(exc):
        params["booting_up"] = True

    return render_template(ERROR_TEMPLATE, request=request, **params)


run_startup_checks(app)
