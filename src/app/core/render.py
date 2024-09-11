import json
from enum import Enum
from typing import Any

from fastapi.requests import Request

from .settings import (
    SERVER_QUERY_PARAM,
    get_server_name,
    get_server_options,
)
from .utils import ContextResponse

RENDER_HELPERS: dict = {}


def register(fn: Any) -> Any:
    """Register a render helper function."""
    global RENDER_HELPERS
    RENDER_HELPERS[fn.__name__] = fn
    return fn


class BootstrapLevel(Enum):
    """Bootstrap levels in UI."""

    SUCCESS = 'success'
    WARNING = 'warning'
    DANGER = 'danger'


@register
def render_response(k: Any, v: Any, add_anchor: bool = False) -> str:
    """Render KSQL response dict."""
    # Do not render @type field
    if k == '@type':
        return ''

    # Skip empty values (but not 0 or False)
    if check_is_empty(v):
        return ''

    v = render_json(v)

    id_tag = f'id="{k}"' if add_anchor else ''
    return f'''
    <div class="resp" {id_tag}>
        <div class="key">{k}</div>
        <div class="value">{v}</div>
    </div>
    '''


@register
def check_is_empty(v: Any) -> bool:
    """Check if value is empty."""
    return v is None or v == [] or v == ''


@register
def render_json(v: Any) -> str:
    """Render JSON data as pre."""
    if isinstance(v, (dict, list)):
        result = json.dumps(v, indent=4)
    else:
        result = str(v)

    return f'<pre class="wrap-pre">{result}</pre>'


@register
def render_topic_link(request: Request, name: str,) -> str:
    """Render topic link (configured in settings)."""
    params = get_server_options(request)
    if link := params.get('topic_link', ''):
        return str(render_link(link.format(name), name))

    return name


@register
def render_stream_link(request: Request, name: str, target: bool = False) -> str:
    """Render topic link (configured in settings)."""
    server_name = get_server_name(request=request)
    href = f'/streams/{name}?{SERVER_QUERY_PARAM}={server_name}'
    return str(render_link(href, name, target))


@register
def render_link(
    href: str,
    text: str,
    target: bool = True,
    style: str = 'font-size: 14px;',
) -> str:
    """Render link."""
    target_blank = 'target="_blank"' if target else ''
    return f'<a href="{href}" class="link-offset-2" style="{style}" {target_blank}>{text}</a>'


@register
def render_level(response: ContextResponse) -> str:
    """Render response level using Bootstrap levels."""
    response_level = BootstrapLevel.SUCCESS.value

    if response.code >= 400:
        response_level = BootstrapLevel.DANGER.value
    elif len(response.data) == 0:
        response_level = BootstrapLevel.WARNING.value
    else:
        for entry in response.data:
            if entry['@type'] == 'warning_entity':
                return BootstrapLevel.WARNING.value

    return response_level
