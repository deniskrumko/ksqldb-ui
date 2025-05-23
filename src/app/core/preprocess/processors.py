import httpx

from .resources import (
    PreprocessedData,
    parse_schema_list,
)


def preprocess_data(response: httpx.Response) -> PreprocessedData | None:
    """Preprocess data from ksqlDB response."""
    if response.status_code != 200:
        return None

    data = response.json()
    if not isinstance(data, list) or not data:
        return None

    if "header" in data[0]:
        return preprocess_select(data)

    return None


def preprocess_select(data: list) -> PreprocessedData:
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

    return PreprocessedData(
        rows=preprocessed_data,
        schema_list=schema_list,
        final_message=data[-1].get("finalMessage"),
    )
