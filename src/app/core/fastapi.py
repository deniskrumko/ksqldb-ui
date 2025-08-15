from collections import deque
from pathlib import Path
from typing import Any

from fastapi import (
    FastAPI,
    Response,
)
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.types import Scope

from app.core.settings import (
    README,
    Settings,
    get_settings,
)
from app.core.utils import get_version


class CacheControlledStaticFiles(StaticFiles):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize class instance."""
        self.max_age = kwargs.pop("max_age", 86400)
        super().__init__(*args, **kwargs)

    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = f"public, max-age={self.max_age}"
        return response


def init_fastapi_app(with_routes: bool = True) -> FastAPI:
    """Initialize FastAPI application with settings and routes."""
    app = FastAPI()
    try:
        settings: Settings = get_settings()
    except Exception as e:
        print(f"\n{e}\n{README}#configuration\n")  # noqa
        raise SystemExit(1)

    app.settings = settings
    if settings.history.enabled:
        app.history = deque(maxlen=settings.history.size)

    static_dir = Path(__file__).parent.parent.parent / "static"
    app.mount("/static", CacheControlledStaticFiles(directory=static_dir), name="static")

    app.app_version = get_version()

    if with_routes:
        register_routes(app)

    return app


def register_routes(app: FastAPI) -> None:
    from app.index import router as index_page
    from app.queries import router as queries_page
    from app.requests import router as requests_page
    from app.status import router as status_page
    from app.streams import router as streams_page
    from app.topics import router as topics_page
    from app.topology import router as topology_page

    for route in (
        index_page,
        queries_page,
        requests_page,
        streams_page,
        status_page,
        topology_page,
        topics_page,
    ):
        app.include_router(route)


def api_error(error: str, success: bool = False, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        content={"success": success, "error": error},
        status_code=status_code,
    )


def api_success(data: Any, success: bool = True, status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        content={"success": success, "data": data},
        status_code=status_code,
    )
