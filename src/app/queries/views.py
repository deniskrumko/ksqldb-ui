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
    query_names = str(form_data["delete_object"])
    if not query_names:
        raise ValueError(_("Query name is not set"))

    for query_name in query_names.split(","):
        query_name = query_name.strip()
        if not query_name:
            continue
        await get_ksql_client(request).execute_statement(f"TERMINATE {query_name}")

    return await list_view(
        request,
        extra_context={
            "deleted_query": query_names,
        },
    )


@router.get("/queries/{query_name}")
async def detail_view(request: Request, query_name: str) -> Response:
    """View to show query details."""
    ksql = get_ksql_client(request)
    response = await ksql.execute_statement(
        f"EXPLAIN {query_name}",
        exc_message=_("Failed to explain query {query_name}. Maybe wrong server?").format(
            query_name=query_name,
        ),
        list_page_url=str(request.url_for("list_view")),
    )

    data = response.json()
    query = data[0]

    status_response = await ksql.execute_statement("SHOW QUERIES")
    if status_response.status_code == 200:
        for listed_query in status_response.json()[0].get("queries", []):
            if listed_query.get("id") == query_name:
                query["statusCount"] = listed_query.get("statusCount", {})
                break
    query.setdefault("statusCount", {})

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
        query_can_control=(
            str(query["queryDescription"].get("queryType", "")).upper() == "PERSISTENT"
        ),
        query_is_paused=int(query["statusCount"].get("PAUSED", 0)) > 0,
        query_tasks=query_tasks,
    )


@router.post("/queries/{query_name}/control")
async def control_query(request: Request, query_name: str) -> Response:
    """Pause or resume a persistent query."""
    form_data = await request.form()
    action = str(form_data.get("action", "")).upper()
    if action not in {"PAUSE", "RESUME"}:
        raise ValueError("Query action must be PAUSE or RESUME")

    ksql = get_ksql_client(request)
    response = await ksql.execute_statement("SHOW QUERIES")
    matching_query = next(
        (query for query in response.json()[0].get("queries", []) if query.get("id") == query_name),
        None,
    )
    if matching_query is None:
        raise ValueError(_("Query {query_name} was not found").format(query_name=query_name))

    await ksql.execute_statement(f"{action} {matching_query['id']}")
    return await detail_view(request, query_name)
