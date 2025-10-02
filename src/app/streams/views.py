from typing import Optional

from fastapi import (
    APIRouter,
    Request,
)
from fastapi.responses import Response

from app.core.i18n import _
from app.core.ksqldb import (
    KSQL_SYSTEM_STREAM,
    get_ksql_client,
)
from app.core.templates import render_template

router = APIRouter()


@router.get("/streams")
async def list_view(request: Request, extra_context: Optional[dict] = None) -> Response:
    """View to list all available streams."""
    response = await get_ksql_client(request).execute_statement("SHOW STREAMS")
    return render_template(
        "streams/list.html",
        request=request,
        response=response,
        streams=sorted(response.json()[0]["streams"], key=lambda x: x["name"]),
        **(extra_context or {}),
    )


@router.post("/streams")
async def delete_stream(request: Request) -> Response:
    """Route to delete a stream."""
    form_data = await request.form()
    stream_names = str(form_data["delete_object"])
    if not stream_names:
        raise ValueError(_("Stream name is not set"))

    for stream_name in stream_names.split(","):
        stream_name = stream_name.strip()
        if not stream_name:
            continue

        if stream_name == KSQL_SYSTEM_STREAM:
            raise ValueError(
                _(
                    "Cannot delete {name} system stream from ksqldb-ui. "
                    "This is a protection measure.",
                ).format(name=KSQL_SYSTEM_STREAM),
            )

        # for some cases we need to quote the stream name
        if stream_name != stream_name.upper():
            stream_name = f'"{stream_name}"'

        await get_ksql_client(request).execute_statement(f"DROP STREAM {stream_name}")

    return await list_view(
        request,
        extra_context={
            "deleted_stream": stream_names,
        },
    )


@router.get("/streams/{stream_name}")
async def detail_view(request: Request, stream_name: str) -> Response:
    """View to show stream details."""
    response = await get_ksql_client(request).execute_statement(
        f"DESCRIBE {stream_name}",
        exc_message=_("Failed to describe stream {stream_name}. Maybe wrong server?").format(
            stream_name=stream_name,
        ),
        list_page_url=str(request.url_for("list_view")),
    )

    return render_template(
        "streams/details.html",
        request=request,
        response=response,
        stream=response.json()[0],
    )
