from dataclasses import dataclass
from typing import Any


@dataclass
class Schema:
    name: str
    type_: str
    fields: list["Schema"] | None = None

    def keys(self) -> list[str]:
        """Return keys of the schema."""
        return ["name", "type", "fields"]

    def get(self, key: str) -> Any:
        """Get value by key."""
        if key == "type":
            return self.type_

        return getattr(self, key)


def parse_schema_list(fields_str: str) -> list[Schema]:
    fields = []
    i = 0
    n = len(fields_str)

    while i < n:
        # Skip whitespace
        while i < n and fields_str[i].isspace():
            i += 1
        # Parse field name
        if i < n and fields_str[i] == "`":
            i += 1
            start = i
            while i < n and fields_str[i] != "`":
                i += 1
            name = fields_str[start:i]
            i += 1  # skip closing `
        else:
            start = i
            while i < n and fields_str[i] not in " ,<":
                i += 1
            name = fields_str[start:i]
        while i < n and fields_str[i].isspace():
            i += 1

        # Parse type
        start = i
        depth = 0
        while i < n:
            if fields_str[i] == "<":
                depth += 1
            elif fields_str[i] == ">":
                if depth == 0:
                    break
                depth -= 1
            elif fields_str[i] == "," and depth == 0:
                break
            i += 1

        type_str = fields_str[start:i].strip()
        nested = None
        type_ = type_str
        if type_str.startswith("STRUCT<"):
            inner = type_str[7:-1]
            type_ = "STRUCT"
            nested = parse_schema_list(inner)
        elif type_str.startswith("ARRAY<"):
            inner = type_str[6:-1].strip()
            type_ = "ARRAY"
            if inner.startswith("STRUCT<"):
                nested = parse_schema_list(inner[7:-1])

        fields.append(
            Schema(
                name=name,
                type_=type_,
                fields=nested,
            ),
        )
        # Skip comma and whitespace
        while i < n and (fields_str[i] == "," or fields_str[i].isspace()):
            i += 1
    return fields


@dataclass
class PreprocessedData:
    rows: list
    schema_list: list[Schema] | None = None
    final_message: str | None = None
