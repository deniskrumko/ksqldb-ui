from datetime import datetime
from typing import Any

from fastapi.requests import Request

from app.core.settings import get_server_name


class RequestHistory:

    def __init__(self, query: str, server_name: str):
        """Initialize class instance."""
        self.query = query
        self.server_name = server_name
        self.date = datetime.now()


def add_request_to_history(request: Request, query: Any) -> None:
    """Add request to history."""
    if request.app.history_enabled:
        entry = RequestHistory(str(query), get_server_name(request) or "-")
        request.app.history.append(entry)
