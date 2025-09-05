from dataclasses import dataclass


@dataclass
class Schema:
    name: str
    type: str
    fields: list["Schema"] | None = None


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
                type=type_,
                fields=nested,
            ),
        )
        # Skip comma and whitespace
        while i < n and (fields_str[i] == "," or fields_str[i].isspace()):
            i += 1
    return fields


@dataclass
class SelectResult:
    rows: list
    schema_list: list[Schema] | None = None
    final_message: str | None = None

    def render(self) -> str:
        """Render preprocessed data."""
        from ..render import (
            Options,
            render_kv,
        )

        result = render_kv(
            "Schema",
            self.schema_list,
            as_table=True,
            show_line_numbers=False,
            options={
                "type": Options(badge=True),
                "fields": Options(hide_empty_column=True),
            },
        )

        for index, row in enumerate(self.rows, start=1):
            result += render_kv(
                k=f"Row {index}/{len(self.rows)}",
                v=row,
                add_copy_button=True,
            )
        result += f'<div class="divider">{self.final_message}</div>'
        return result


@dataclass
class TableRenderer:
    items: list[dict]
    cols: list[str] | None = None
    options: dict[str, str] | None = None

    def render(self) -> str:
        from ..render import render_table

        return render_table(self.items, cols=self.cols, options=self.options)  # type: ignore


@dataclass
class RawRenderer:
    data: str

    def render(self) -> str:
        return self.data
