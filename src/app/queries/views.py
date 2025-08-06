from typing import Optional

from fastapi import (
    APIRouter,
    Request,
)
from fastapi.responses import Response

from app.core.i18n import _
from app.core.ksqldb import get_ksql_client
from app.core.templates import render_template

router = APIRouter()


@router.get("/queries")
async def list_view(request: Request, extra_context: Optional[dict] = None) -> Response:
    """View to list all available queries."""
    ksql = get_ksql_client(request)
    response = await ksql.execute_statement("SHOW QUERIES")
    return render_template(
        "queries/list.html",
        request=request,
        response=response,
        queries=sorted(response.json()[0]["queries"], key=lambda x: x["id"]),
        **(extra_context or {}),
    )


@router.post("/queries")
async def delete_query(request: Request) -> Response:
    """Route to delete a query."""
    form_data = await request.form()
    query_name = form_data["delete_object"]
    if not query_name:
        raise ValueError(_("Query name is not set"))

    await get_ksql_client(request).execute_statement(f"TERMINATE {query_name}")
    return await list_view(
        request,
        extra_context={
            "deleted_query": query_name,
        },
    )


@router.get("/queries/{query_name}")
async def detail_view(request: Request, query_name: str) -> Response:
    """View to show query details."""
    response = await get_ksql_client(request).execute_statement(
        f"EXPLAIN {query_name}",
        exc_message=_("Failed to explain query {query_name}. Maybe wrong server?").format(
            query_name=query_name,
        ),
        list_page_url=str(request.url_for("list_view")),
    )

    data = response.json()
    query = data[0]

    try:
        query_tasks = sorted(
            [
                {
                    "id": task["taskId"],
                    "topic": task["topicOffsets"][0]["topicPartitionEntity"]["topic"],
                    "partition": task["topicOffsets"][0]["topicPartitionEntity"]["partition"],
                    "end Offset": task["topicOffsets"][0]["endOffset"],
                    "committed Offset": task["topicOffsets"][0]["committedOffset"],
                }
                for task in query["queryDescription"].get("tasksMetadata", [])
            ],
            key=lambda x: x["id"],
        )
    except Exception:
        query_tasks = []

    return render_template(
        "queries/details.html",
        request=request,
        response=response,
        query=query,
        query_tasks=query_tasks,
    )
