from datetime import datetime
from typing import Any

from fastapi.requests import Request

from app.core.settings import get_server


class RequestHistory:

    def __init__(self, query: str, server_code: str):
        """Initialize class instance."""
        self.query = query
        self.server_code = server_code
        self.date = datetime.now()


def add_request_to_history(request: Request, query: Any) -> None:
    """Add request to history."""
    if request.app.settings.history.enabled:
        entry = RequestHistory(
            query=str(query),
            server_code=get_server(request).code,
        )
        request.app.history.append(entry)
