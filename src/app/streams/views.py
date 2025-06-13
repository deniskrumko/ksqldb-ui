from typing import Optional

from fastapi import (
    APIRouter,
    Request,
)
from fastapi.responses import Response

from app.core.ksqldb import (
    KSQL_SYSTEM_STREAM,
    KsqlException,
    KsqlRequest,
)
from app.core.templates import render_template

router = APIRouter()


@router.get("/streams")
async def list_view(request: Request, extra_context: Optional[dict] = None) -> Response:
    """View to list all available streams."""
    response = await KsqlRequest(request, "SHOW STREAMS").execute()
    if not response.is_success:
        raise KsqlException("Failed to show streams", response)

    data = response.json()
    return render_template(
        "streams/list.html",
        request=request,
        response=response,
        streams=sorted(data[0]["streams"], key=lambda x: x["name"]),
        **(extra_context or {}),
    )


@router.post("/streams")
async def delete_stream(request: Request) -> Response:
    """Route to delete a stream."""
    form_data = await request.form()
    stream_name = str(form_data["delete_object"])
    if not stream_name:
        raise ValueError("Stream name is not set")

    if stream_name == KSQL_SYSTEM_STREAM:
        raise ValueError(
            f"Cannot delete {KSQL_SYSTEM_STREAM} system stream from ksqldb-ui. "
            "This is a protection measure.",
        )

    # for some cases we need to quote the stream name
    if stream_name != stream_name.upper():
        stream_name = f'"{stream_name}"'

    response = await KsqlRequest(request, f"DROP STREAM {stream_name}").execute()
    if not response.is_success:
        raise KsqlException(
            f"Failed to drop stream {stream_name}",
            response=response,
        )

    return await list_view(
        request,
        extra_context={
            "deleted_stream": stream_name,
        },
    )


@router.get("/streams/{stream_name}")
async def detail_view(request: Request, stream_name: str) -> Response:
    """View to show stream details."""
    response = await KsqlRequest(request, f"DESCRIBE {stream_name}").execute()
    if not response.is_success:
        raise KsqlException(
            f"Failed to describe stream {stream_name}. Maybe wrong server?",
            response=response,
            list_page_url=str(request.url_for("list_view")),
        )

    data = response.json()
    return render_template(
        "streams/details.html",
        request=request,
        response=response,
        stream=data[0],
    )
