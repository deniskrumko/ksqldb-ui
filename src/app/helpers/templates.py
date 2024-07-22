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
    templates = Jinja2Templates(directory=templates_dir)

    from .render import RENDER_HELPERS
    templates.env.globals.update(**RENDER_HELPERS)

    TEMPLATES = templates
    return templates


def render_template(template_name: str, request: Request, **kwargs: Any) -> TemplateResponse:
    templates = get_templates()
    return templates.TemplateResponse(template_name, context={'request': request, **kwargs})
