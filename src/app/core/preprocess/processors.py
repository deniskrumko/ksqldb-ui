from typing import (
    Protocol,
    runtime_checkable,
)

import httpx

from .resources import (
    SelectResult,
    TableRenderer,
    parse_schema_list,
)


@runtime_checkable
class Renderable(Protocol):
    def render(self) -> str:
        pass


def preprocess_data(response: httpx.Response) -> Renderable | None:
    """Preprocess data from ksqlDB response."""
    if response.status_code != 200:
        return None

    data = response.json()
    if not isinstance(data, list) or not data:
        return None

    if "header" in data[0]:
        return preprocess_select(data)

    resp_type = data[0].get("@type")
    if resp_type == "function_names":
        return TableRenderer(items=data[0]["functions"], options={"type": "badge"})

    if resp_type == "properties":
        return TableRenderer(items=data[0]["properties"])

    if resp_type == "queries":
        return TableRenderer(
            items=data[0]["queries"],
            cols=[
                "id",
                "queryType",
                "state",
                "sinks",
                "sinkKafkaTopics",
                "queryString",
            ],
            options={
                "queryString": "collapse",
                "queryType": "badge",
                "state": "badge",
            },
        )

    if resp_type == "streams":
        return TableRenderer(
            items=data[0]["streams"],
            options={
                "keyFormat": "badge",
                "valueFormat": "valueFormat",
            },
        )

    return None


def preprocess_select(data: list) -> SelectResult:
    """Preprocess SELECT query data from ksqlDB response."""
    # Extract schema from header
    header = data[0].get("header", {})
    # Extract column names from schema string
    schema_list = parse_schema_list(header.get("schema", ""))

    preprocessed_data = []
    for item in data[1:]:
        row = item.get("row", {}).get("columns", [])
        if row:
            preprocessed_row = {col.name: val for col, val in zip(schema_list, row)}
            preprocessed_data.append(preprocessed_row)

    return SelectResult(
        rows=preprocessed_data,
        schema_list=schema_list,
        final_message=data[-1].get("finalMessage"),
    )
