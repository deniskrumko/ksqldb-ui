from pathlib import Path
from typing import (
    Any,
    Optional,
)

from fastapi import Request
from fastapi.templating import Jinja2Templates
from httpx._models import Response as HttpxResponse
from starlette.templating import _TemplateResponse as TemplateResponse

from .i18n import get_translations
from .settings import get_server_code
from .utils import (
    CONTEXT_REQUEST_KEY,
    CONTEXT_RESPONSE_KEY,
    ContextRequest,
    ContextResponse,
)

TEMPLATES: Optional[Jinja2Templates] = None
ERROR_TEMPLATE = "error.html"
ERROR_NO_SERVER_TEMPLATE = "error_no_server.html"


def get_templates() -> Jinja2Templates:
    """Get Jinja2Templates instance."""
    global TEMPLATES

    if TEMPLATES is not None:
        return TEMPLATES

    templates_dir = Path(__file__).parent.parent.parent / "templates"
    templates = Jinja2Templates(directory=templates_dir)

    from .render import RENDER_HELPERS

    templates.env.globals.update(**RENDER_HELPERS)
    templates.env.add_extension("jinja2.ext.i18n")

    # Устанавливаем переводы
    translations = get_translations()
    templates.env.install_gettext_translations(translations)

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

    if base_context := get_base_context(request):
        context.update(base_context)
    else:
        template_name = ERROR_NO_SERVER_TEMPLATE
        context["code"] = get_server_code(request, raise_exc=False)

    return templates.TemplateResponse(template_name, context=context)


def get_base_context(request: Request) -> dict:
    """Base context for all templates."""
    from .settings import (
        SERVER_QUERY_PARAM,
        get_server,
    )

    try:
        server = get_server(request)
        return {
            "current_server": server,
            "warning_message": server.warning_message,
            "server_query_param": SERVER_QUERY_PARAM,
            "q": server.query,
        }
    except Exception:
        return {}
