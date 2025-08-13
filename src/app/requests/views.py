from fastapi import (
    APIRouter,
    Request,
)
from starlette.datastructures import UploadFile
from starlette.responses import Response

from app.core.fastapi import (
    api_error,
    api_success,
)
from app.core.ksqldb import get_ksql_client
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

        ksql = get_ksql_client(request)
        ksql_response = await ksql.execute_statement_then_query(str(query))
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


@router.post("/api/process_file")
async def api_process_file(request: Request) -> Response:
    """API endpoint to process uploaded file as ksqlDB query."""
    form_data = await request.form()
    uploaded_file = form_data.get("file")

    if not uploaded_file or not isinstance(uploaded_file, UploadFile):
        return api_error("No file uploaded", status_code=400)

    # Read file content
    file_content = await uploaded_file.read()
    query = file_content.decode("utf-8").strip()

    if not query:
        return api_error("File is empty", status_code=400)

    try:
        # Execute query
        ksql = get_ksql_client(request)
        ksql_response = await ksql.execute_statement_then_query(query)
        return api_success(
            {
                "query": query,
                "response": ksql_response.json(),
            },
        )
    except Exception as e:
        return api_error(f"Failed to process file: {repr(e)}", status_code=500)
