import contextlib
import datetime
import json
from dataclasses import dataclass
from enum import Enum
from typing import (
    Any,
    Callable,
    TypeVar,
)

from fastapi.requests import Request

from .ksqldb import KsqlErrors
from .settings import (
    SERVER_QUERY_PARAM,
    get_server,
    get_server_options,
)
from .utils import ContextResponse

RENDER_HELPERS: dict = {}

TABLE_TEMPLATE = """
<div class="table-container">
    <table class="table">
    <thead>
        <tr>{columns}</tr>
    </thead>
    <tbody>{body}</tbody>
    </table>
</div>
"""

BUBBLE_TEMPLATE = """
<div class="bubble">
    <div class="bubble-heading">{heading}</div>
    <div class="bubble-body">{body}</div>
</div>
"""

F = TypeVar("F", bound=Callable[..., Any])


def register(fn: F) -> F:
    """Register a render helper function."""
    global RENDER_HELPERS  # noqa
    RENDER_HELPERS[fn.__name__] = fn
    return fn


class BootstrapLevel(Enum):
    """Bootstrap levels in UI."""

    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"


@register
def render_map(response: dict, **kwargs: Any) -> str:
    if (
        response.get("error_code") == KsqlErrors.BAD_STATEMENT.value
    ) and "Syntax Error" in response.get("message", ""):
        return str(render_syntax_error_response(response, **kwargs))

    result = ""
    for k, v in response.items():
        result += render_kv(k, v, **kwargs)

    return result


@register
def render_list(value: list | tuple) -> str:
    return "<br>".join(render_value(v) for v in value)


@dataclass
class Options:
    badge: bool = False
    ignored: bool = False
    breaked: bool = False
    timestamp: bool = False
    kafka_topic: bool = False

    @classmethod
    def from_string(cls, value: str) -> "Options":
        return cls(
            badge=any(v in value for v in ["badge", "pill"]),
            ignored=any(v in value for v in ["hide", "ignore", "ignored"]),
            breaked=any(v in value for v in ["br", "break", "breaked"]),
            timestamp=any(v in value for v in ["timestamp", "ts"]),
            kafka_topic=any(v in value for v in ["topic", "kafka_topic"]),
        )


@register
def render_timestamp(value: Any, container: str = "i", **kwargs: Any) -> str:
    """Render timestamp as string."""
    timestamp = int(value)
    date = datetime.datetime.fromtimestamp(timestamp / 1000)
    return f'<{container}>{date.strftime("%Y-%m-%d %H:%M:%S")}</{container}>' if timestamp else ""


@register
def render_value(
    value: Any,
    options: Options | None = None,
    parent_options: dict[str, Any] | None = None,
    **kwargs: Any,
) -> str:
    opt = options or Options()

    if opt.kafka_topic:
        return render_topic_link(
            request=kwargs["request"],
            name=value,
        )

    if opt.timestamp:
        return render_timestamp(value)

    if opt.badge:
        return f'<span class="badge text-bg-purple">{value}</span>'

    if value is True or (isinstance(value, str) and value.lower() == "true"):
        return '<span class="badge text-bg-success">true</span>'

    if value is False or (isinstance(value, str) and value.lower() == "false"):
        return '<span class="badge text-bg-danger">false</span>'

    if value == "[hidden]" or value is None:
        value = str(value).lstrip("[").rstrip("]").lower()
        return f'<span class="badge text-bg-secondary">{value}</span>'

    if isinstance(value, (int, float)):
        return f"<code>{value}</code>"

    if isinstance(value, str) and (value.isdigit() or value[1:].isdigit()):
        return f"<code>{value}</code>"

    if isinstance(value, (list, tuple)):
        if value and isinstance(value[0], dict):
            return render_table(list(value), **(parent_options or {}))

        return render_list(value)

    if isinstance(value, dict):
        return render_map(value, **(parent_options or {}))

    return str(value)


@register
def render_table(
    data: list[Any],
    cols: list[str] | None = None,
    show_line_numbers: bool = True,
    options: dict[str, str | Options] | None = None,
    **kwargs: Any,
) -> str:
    """Render a table.

    :param data: list of dicts with data
    :param cols: list of columns to display. If None, then autodetect columns from first entry.
    :param options: formatting options for each col
    """
    if not data:
        return ""

    opts: dict[str, Options] = {
        k: Options.from_string(v) if isinstance(v, str) else v for k, v in (options or {}).items()
    }

    columns_keys = cols or list(data[0].keys())
    columns = '<th scope="col">#</th>' if show_line_numbers else ""
    for col in columns_keys:
        if col in opts and opts[col].ignored:
            continue

        columns += f'\n<th scope="col">{col.title()}</th>'

    body = ""
    for i, item in enumerate(data, start=1):
        item_body = f'<th scope="row">{i}</th>' if show_line_numbers else ""
        for col in columns_keys:
            opt = opts.get(col, Options())
            if opt.ignored:
                continue

            td_class = ""
            if opt.breaked:
                td_class += "breaked"

            value = render_value(
                value=item.get(col),
                options=opt,
                parent_options={
                    "cols": cols,
                    "show_line_numbers": show_line_numbers,
                    "options": options,
                    "as_table": True,
                },
                **kwargs,
            )
            item_body += f"\n<td class={td_class}>{value}</td>"

        body += f"<tr>{item_body}</tr>"

    return TABLE_TEMPLATE.format(columns=columns, body=body)


@register
def render_syntax_error_response(response: dict) -> str:
    query = response["statementText"]
    err_line, err_pos, *rest = response["message"].split(":")
    if err_line != "line 1":
        raise ValueError('Unexpected line number, should be "line 1"')

    position = int(err_pos) - 1
    query = render_json(f'{query[:position]}<span class="error-highlight">{query[position:]}<span>')

    result = f"""
    <div class="resp">
        <h2>Invalid syntax at position {position}</h2>
        <div class="key">Query</div>
        <div>{query}</div>
    </div>
    """

    with contextlib.suppress(Exception):
        parts = "".join(rest).strip().split("\n")
        result += render_kv(parts[0], "<br>".join(parts[1:]))

    return result


@register
def render_kv(
    k: Any,
    v: Any,
    add_anchor: bool = False,
    as_table: bool = False,
    **kwargs: Any,
) -> str:
    """Render KSQL response dict."""
    # Do not render @type field
    if k == "@type":
        return ""

    # Skip empty values (but not 0 or False)
    if check_is_empty(v):
        return ""

    if as_table and isinstance(v, (list, tuple)):
        v = render_table(list(v))
    else:
        v = render_json(v)

    id_tag = f'id="{k}"' if add_anchor else ""
    return f"""
    <div class="resp" {id_tag}>
        <div class="key">{k}</div>
        <div class="value">{v}</div>
    </div>
    """


@register
def check_is_empty(v: Any) -> bool:
    """Check if value is empty."""
    return v is None or v == [] or v == ""


@register
def render_json(v: Any) -> str:
    """Render JSON data as pre."""
    if isinstance(v, (dict, list)):
        result = json.dumps(v, indent=4)
    else:
        result = str(v)

    return f'<pre class="wrap-pre">{result}</pre>'


@register
def render_topic_link(
    request: Request,
    name: str,
    **kwargs: Any,
) -> str:
    """Render topic link (configured in settings)."""
    params = get_server_options(request)
    if link := params.get("topic_link", ""):
        return str(render_link(link.format(name), name, **kwargs))

    return name


@register
def render_stream_link(request: Request, name: str, target: bool = False) -> str:
    """Render topic link (configured in settings)."""
    server_name = get_server(request=request)
    href = f"/streams/{name}?{SERVER_QUERY_PARAM}={server_name}"
    return str(render_link(href, name, target))


@register
def render_link(
    href: str,
    text: str,
    target: bool = True,
    classes: str = "link-offset-2 link-sm breaked",
) -> str:
    """Render link."""
    target_blank = 'target="_blank"' if target else ""
    return f'<a href="{href}" class="{classes}" {target_blank}>{text}</a>'


@register
def render_level(response: ContextResponse) -> str:
    """Render response level using Bootstrap levels."""
    response_level = BootstrapLevel.SUCCESS.value

    if response.code >= 400:
        response_level = BootstrapLevel.DANGER.value
    elif len(response.data) == 0 and not response.text:
        response_level = BootstrapLevel.WARNING.value
    else:
        for entry in response.data:
            if entry.get("@type") == "warning_entity":
                return BootstrapLevel.WARNING.value

    return response_level


@register
def render_bubbles(data: dict, keys: list[str] | None = None, lower: bool = False) -> str:
    def render(k: Any) -> str:
        v = data.get(k)
        if lower:
            v = str(v).lower()
        return BUBBLE_TEMPLATE.format(heading=k, body=v)

    keys = keys or list(data)
    return "".join(render(k) for k in keys)


@register
def render_stream_fields(data: list) -> str:
    def flatten(item: dict | list | None) -> dict | list | None:
        if not item:
            return None
        elif isinstance(item, list):
            return [flatten(i) for i in item]
        else:
            result = {
                "name": item["name"],
                "type": item.get("type", item["schema"]["type"]),
            }
            if fields := item["schema"].get("fields"):
                result["fields"] = flatten(fields)
            return result

    return render_table(
        [flatten(item) for item in data],
        cols=["name", "type", "fields"],
        options={
            "type": Options(badge=True),
        },
    )
