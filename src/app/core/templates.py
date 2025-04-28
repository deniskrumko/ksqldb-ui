from pathlib import Path
from typing import (
    Any,
    Optional,
)

from fastapi import Request
from fastapi.templating import Jinja2Templates
from httpx._models import Response as HttpxResponse
from starlette.templating import _TemplateResponse as TemplateResponse

from .utils import (
    CONTEXT_REQUEST_KEY,
    CONTEXT_RESPONSE_KEY,
    ContextRequest,
    ContextResponse,
)

TEMPLATES: Optional[Jinja2Templates] = None


def get_templates() -> Jinja2Templates:
    """Get Jinja2Templates instance."""
    global TEMPLATES

    if TEMPLATES is not None:
        return TEMPLATES

    templates_dir = Path(__file__).parent.parent.parent / "templates"
    templates = Jinja2Templates(directory=templates_dir, context_processors=[base_context])

    from .render import RENDER_HELPERS

    templates.env.globals.update(**RENDER_HELPERS)

    TEMPLATES = templates
    return templates


def render_template(
    template_name: str,
    request: Request,
    response: Optional[HttpxResponse] = None,
    **kwargs: Any,
) -> TemplateResponse:
    """Render template by name and context."""
    templates = get_templates()
    context = {"request": request, **kwargs}

    # Convert httpx.Response to context dict.
    if response is not None:
        context[CONTEXT_RESPONSE_KEY] = ContextResponse(response)
        context[CONTEXT_REQUEST_KEY] = ContextRequest(response.request)

    return templates.TemplateResponse(template_name, context=context)


def base_context(request: Request) -> dict:
    """Base context for all templates."""
    from .settings import (
        SERVER_QUERY_PARAM,
        get_server_name,
        get_server_options,
        get_server_url,
    )

    server_name = get_server_name(request)
    server_options = get_server_options(request)
    return {
        "current_server": server_name,
        "current_server_url": get_server_url(request, server_options),
        "warning_message": server_options.get("warning_message"),
        "server_query_param": SERVER_QUERY_PARAM,
        "q": f"{SERVER_QUERY_PARAM}={server_name}",
    }
