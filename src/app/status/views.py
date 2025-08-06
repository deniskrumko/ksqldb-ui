from fastapi import (
    APIRouter,
    Request,
)
from fastapi.responses import Response

from app.core.ksqldb import get_ksql_client
from app.core.templates import render_template

router = APIRouter()


@router.get("/status")
async def get_server_status(request: Request) -> Response:
    """View to list all available queries."""
    ksql = get_ksql_client(request)
    info = await ksql.get_info()
    health = await ksql.get_health()
    properties = await ksql.execute_statement("SHOW PROPERTIES;")
    return render_template(
        "status/index.html",
        request,
        info=info.json(),
        health=health.json(),
        properties=properties.json()[0]["properties"],
        response=properties,
    )


@router.get("/debug")
async def debug_page(request: Request) -> Response:
    """Debug page."""
    return render_template("status/debug.html", request)
