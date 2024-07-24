from pathlib import Path
from typing import (
    Any,
    Optional,
)

from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse as TemplateResponse

TEMPLATES: Optional[Jinja2Templates] = None


def get_templates() -> Jinja2Templates:
    global TEMPLATES

    if TEMPLATES is not None:
        return TEMPLATES

    templates_dir = Path(__file__).parent.parent.parent / 'templates'
    templates = Jinja2Templates(directory=templates_dir, context_processors=[extra_context])

    from .render import RENDER_HELPERS
    templates.env.globals.update(**RENDER_HELPERS)

    TEMPLATES = templates
    return templates


def render_template(template_name: str, request: Request, **kwargs: Any) -> TemplateResponse:
    templates = get_templates()
    return templates.TemplateResponse(template_name, context={'request': request, **kwargs})


def extra_context(request: Request) -> dict:
    from .settings import (
        SERVER_QUERY_PARAM,
        get_server_name,
        get_server_url,
    )

    server_name = get_server_name(request)
    return {
        'current_server': server_name,
        'current_server_url': get_server_url(request),
        'server_query_param': SERVER_QUERY_PARAM,
        'q': f'{SERVER_QUERY_PARAM}={server_name}',
    }
