import contextlib
import dataclasses
import datetime
import json
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import (
    Any,
    Callable,
    TypeVar,
)

from fastapi.requests import Request

from .ksqldb import KsqlErrors
from .settings import get_server
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
def render_section(response: dict, **kwargs: Any) -> str:
    if (
        response.get("error_code") == KsqlErrors.BAD_STATEMENT.value
    ) and "Syntax Error" in response.get("message", ""):
        return str(render_syntax_error_response(response, **kwargs))

    result = ""
    for k, v in response.items():
        result += render_kv(k, v, **kwargs)

    return result


@register
def render_list(value: list | tuple, enum: bool = False) -> str:
    """Render plain list."""
    rendered_values = (render_value(v) for v in value)
    if enum:
        rendered_values = (f"{i}. {val}" for i, val in enumerate(rendered_values, start=1))

    return "<br>".join(rendered_values)


@dataclass
class Options:
    # Wrap as code
    code: bool = False

    # Render as badge
    badge: bool = False

    # Don't display value
    ignored: bool = False

    # Word break
    breaked: bool = False

    # Render timestamp as datetime
    timestamp: bool = False

    # Render kafka topic as link
    kafka_topic: bool = False

    # Render as collapsible element
    collapsible: bool = False

    # Hide table elements if empty
    hide_empty_column: bool = False

    @classmethod
    def from_string(cls, value: str) -> "Options":
        return cls(
            code=any(v in value for v in ["code", "pre"]),
            badge=any(v in value for v in ["badge", "pill"]),
            ignored=any(v in value for v in ["hide", "ignore", "ignored"]),
            breaked=any(v in value for v in ["br", "break", "breaked"]),
            timestamp=any(v in value for v in ["timestamp", "ts"]),
            kafka_topic=any(v in value for v in ["topic", "kafka_topic"]),
            collapsible=any(v in value for v in ["collapsible", "collapse"]),
            hide_empty_column=any(v in value for v in ["empty_column"]),
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
    options: Options | str | None = None,
    parent_options: dict[str, Any] | None = None,
    **kwargs: Any,
) -> str:
    if isinstance(options, str):
        opt = Options.from_string(options)
    else:
        opt = options or Options()

    if opt.code:
        return f"<code>{value}</code>"

    if opt.kafka_topic:
        return render_topic_link(
            request=kwargs["request"],
            name=value,
        )

    if opt.timestamp:
        return render_timestamp(value)

    if opt.badge:
        return f'<span class="badge text-bg-purple">{value}</span>'

    if opt.collapsible:
        return f"<details><summary>Collapsed</summary>{value}</details>"

    if hasattr(value, "render"):
        return str(value.render())

    if value is True or (isinstance(value, str) and value.lower() == "true"):
        return '<span class="badge text-bg-success">true</span>'

    if value is False or (isinstance(value, str) and value.lower() == "false"):
        return '<span class="badge text-bg-danger">false</span>'

    if value == "[hidden]" or value is None:
        value = str(value).lstrip("[").rstrip("]").lower()
        return f'<span class="badge text-bg-secondary">{value}</span>'

    if isinstance(value, (int, float)):
        return f"<code>{value}</code>"

    if isinstance(value, str):
        if value.isdigit() or value[1:].isdigit():
            return f"<code>{value}</code>"

        if value.startswith("http://") or value.startswith("https://"):
            return render_link(value, classes="link-offset-2")

    if isinstance(value, (list, tuple)):
        if value and (isinstance(value[0], dict) or dataclasses.is_dataclass(value[0])):
            return render_table(list(value), **(parent_options or {}))

        return render_list(value)

    # TODO: Maybe change to different renderer
    if isinstance(value, dict):
        return render_section(value, **(parent_options or {}))

    if isinstance(value, deque):
        value = list(reversed(value))
        if value and hasattr(value[0], "keys"):
            return render_table(value)
        else:
            return render_list(value)

    return str(value)


@register
def render_dict_table(data: dict, **kwargs: Any) -> str:
    return render_table(
        data=[{"key": k, "value": v} for k, v in data.items()],
        cols=["key", "value"],
        **kwargs,
    )


@register
def render_list_table(data: list, col_name: str = "value", **kwargs: Any) -> str:
    return render_table(
        data=[{col_name: v} for v in data],
        cols=[col_name],
        **kwargs,
    )


@register
def render_table(
    data: list[Any] | None,
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

    def get_value(obj: object, name: str) -> Any:
        if dataclasses.is_dataclass(obj):
            return getattr(obj, name)
        return obj.get(name)

    if not data:
        return ""

    first_el = data[0]
    opts: dict[str, Options] = {
        k: Options.from_string(v) if isinstance(v, str) else v for k, v in (options or {}).items()
    }

    columns_keys = cols
    if not columns_keys:
        if hasattr(first_el, "keys"):
            columns_keys = list(first_el.keys())
        elif dataclasses.is_dataclass(first_el):
            columns_keys = [field.name for field in dataclasses.fields(first_el)]
        else:
            raise TypeError(f"Object of type {type(first_el)} has no methods keys()")

    filtered_columns_keys = []
    columns = '<th scope="col">#</th>' if show_line_numbers else ""
    for col in columns_keys:
        if opt := opts.get(col):
            if opt.ignored:
                continue
            if opt.hide_empty_column:
                if not any(get_value(item, col) for item in data):
                    continue

        columns += f'\n<th scope="col">{col.title()}</th>'
        filtered_columns_keys.append(col)

    body = ""
    for i, item in enumerate(data, start=1):
        item_body = f'<th scope="row">{i}</th>' if show_line_numbers else ""
        for col in filtered_columns_keys:
            opt = opts.get(col, Options())
            td_class = ""
            if opt.breaked:
                td_class += "breaked"

            rendered_value = render_value(
                value=get_value(item, col),
                options=opt,
                parent_options={
                    "cols": cols,
                    "show_line_numbers": show_line_numbers,
                    "options": options,
                    "as_table": True,
                },
                **kwargs,
            )
            item_body += f"\n<td class={td_class}>{rendered_value}</td>"

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
    add_copy_button: bool = False,
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
        v = render_table(list(v), **kwargs)
    else:
        v = render_json(v)

    k_buttons = ""
    if add_copy_button:
        k_buttons += """
        <img src="/static/icons/copy.png" alt="Copy" onclick="copyRespValue(this)"
        class="request-btn"
        data-toggle="tooltip" data-placement="top" title="Copy">
        """

    id_tag = f'id="{k}"' if add_anchor else ""
    return f"""
    <div class="resp" {id_tag}>
        <div class="key">
            {k}
            <div class="resp-key-buttons">
            {k_buttons}
            </div>
        </div>
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
    server = get_server(request)
    if server.topic_link:
        return str(render_link(server.topic_link.format(name), name, **kwargs))

    return name


@register
def render_stream_link(request: Request, name: str, target: bool = False) -> str:
    """Render topic link (configured in settings)."""
    server = get_server(request)
    href = f"/streams/{name}?{server.query}"
    return str(render_link(href, name, target))


@register
def render_link(
    href: str,
    text: str | None = None,
    target: bool = True,
    classes: str = "link-offset-2 link-sm breaked",
) -> str:
    """Render link."""
    target_blank = 'target="_blank"' if target else ""
    return f'<a href="{href}" class="{classes}" {target_blank}>{text or href}</a>'


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
            "fields": Options(hide_empty_column=True),
        },
    )
