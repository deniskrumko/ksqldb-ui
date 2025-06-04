import traceback
from collections import deque
from pathlib import Path
from typing import (
    Any,
    Callable,
)

import httpx
from fastapi import (
    FastAPI,
    Request,
    Response,
)
from starlette.responses import RedirectResponse

from app.core.fastapi import CacheControlledStaticFiles
from app.core.ksqldb.resources import KsqlException
from app.core.settings import (
    README,
    Server,
    Settings,
    get_server_code,
    get_settings,
)
from app.core.templates import (
    ERROR_TEMPLATE,
    render_template,
)
from app.core.utils import make_list

app = FastAPI()

try:
    settings: Settings = get_settings()
except Exception as e:
    print(f"\n{e}\n{README}#configuration\n")  # noqa
    raise SystemExit(1)

app.settings = settings
if settings.history.enabled:
    app.history = deque(maxlen=settings.history.size)

static_dir = Path(__file__).parent.parent / "static"
app.mount("/static", CacheControlledStaticFiles(directory=static_dir), name="static")


def register_routes() -> None:
    from app.index import router as index_page
    from app.queries import router as queries_page
    from app.requests import router as requests_page
    from app.status import router as status_page
    from app.streams import router as streams_page
    from app.topics import router as topics_page

    for route in (
        index_page,
        queries_page,
        requests_page,
        streams_page,
        status_page,
        topics_page,
    ):
        app.include_router(route)


register_routes()


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
