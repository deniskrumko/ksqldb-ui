from fastapi import (
    APIRouter,
    Request,
)
from starlette.responses import Response

from app.core.ksqldb import KsqlRequest
from app.core.preprocess import preprocess_data
from app.core.templates import render_template

from .resources import add_request_to_history

router = APIRouter()


@router.get("/requests")
async def show_request_editor(request: Request) -> Response:
    """View to show request editor."""
    return render_template("requests/index.html", request)


@router.post("/requests")
async def perform_request(request: Request) -> Response:
    """Perform request to ksqlDB server."""
    form_data = await request.form()
    context: dict = {}

    ksql_response = None
    if query := form_data["query"]:
        add_request_to_history(request, query)

        ksql_request = KsqlRequest(request, query)
        ksql_response = await ksql_request.execute(query_fallback=True)
        context["query"] = query

        try:
            context["preprocessed_data"] = preprocess_data(ksql_response)
        except Exception as e:
            context["preprocess_error"] = repr(e)
    else:
        context["warning_msg"] = "Query is empty"

    return render_template(
        "requests/index.html",
        request=request,
        response=ksql_response,
        **context,
    )


@router.get("/history")
async def show_history(request: Request) -> Response:
    """View to show requests history."""
    history = []
    if request.app.settings.history.enabled:
        history = list(reversed(request.app.history))

    return render_template(
        "requests/history.html",
        request=request,
        history=history,
    )


@router.post("/history")
async def delete_history(request: Request) -> Response:
    """View to delete requests history."""
    request.app.history.clear()
    return await show_history(request)
