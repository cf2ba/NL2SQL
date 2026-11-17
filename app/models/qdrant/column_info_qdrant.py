from typing import TypedDict


class ColumnInfoQdrant(TypedDict):
    id: str
    name: str
    type: str
    role: str
    description: str
    examples: list
    alias: list
    table_id: str
