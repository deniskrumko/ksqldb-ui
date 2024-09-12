from typing import Any

from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from starlette.types import Scope


class CacheControlledStaticFiles(StaticFiles):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize class instance."""
        self.max_age = kwargs.pop("max_age", 86400)
        super().__init__(*args, **kwargs)

    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = f"public, max-age={self.max_age}"
        return response
